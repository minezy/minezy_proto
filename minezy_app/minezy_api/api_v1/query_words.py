import time
from minezy_api import app
from minezy_api import neo4j_conn
from query_common import prepare_date_range, prepare_date_clause


def query_words(account, params, countResults=False):

    t0 = time.time()

    if params['rel'] == 'SENDER':
        relL = 'SENT'
        relR = 'TO|CC|BCC'
    elif params['rel'] == 'RECEIVER':
        relL = 'TO|CC|BCC'
        relR = 'SENT'
    else:
        relL = 'SENT|TO|CC|BCC'
        relR = 'SENT|TO|CC|BCC'

    params['ymd'],bYear,bMonth,bDay = prepare_date_range(params)

    bPreCountedSum = False
    query_str = ''
    if len(params['left']) or len(params['right']):
        
        if len(params['left']) and len(params['right']):
            query_str = "MATCH (cL:{0}Contact)-[rL:"+relL+"]-(e:{0}Email)-[rR:"+relR+"]-(cR:{0}Contact),(e)-[r:`WORDS`]-(w:{0}Word)"
            query_str += " WHERE cL.email IN {{left}} AND cR.email IN {{right}} "
            query_str += "AND (type(rL)='SENT' OR type(rR)='SENT') "            
        elif len(params['left']):
            query_str = "MATCH (m:{0}Contact)-[rL:"+relL+"]-(e:{0}Email)-[r:WORDS]-(w:{0}Word) "
            query_str += "WHERE m.email IN {{left}} "
        else:
            query_str = "MATCH (m:{0}Contact)-[rL:"+relL+"]-(e:{0}Email)-[rR:"+relR+"]-(n:{0}Contact) "
            query_str += "WHERE m.email IN {{right}} "
            query_str += "AND (type(rL)='SENT' OR type(rR)='SENT') "
            
        if len(params['ymd']):
            query_str += "WITH n,e MATCH "
            query_str += prepare_date_clause(bYear, bMonth, bDay)
            
    elif len(params['ymd']):
        query_str = "MATCH (w:{0}Word)-[r:WORDS]-(e:{0}Email)"
        query_str += prepare_date_clause(bYear, bMonth, bDay, bNode=False)
        
    else:
        query_str = "MATCH (w:Word)"
        bPreCountedSum = True

    if params['keyword']:
        if not bWhere:
            query_str += "WHERE "
        else:
            query_str += "AND "
        query_str += "w.id =~ '(?i).*"+params['keyword']+".*' "

    if bPreCountedSum:
        query_str += "WITH w,w.count as sum "
    else:    
        query_str += "WITH w,sum(r.count) as sum "

    query_str += "RETURN w.id,sum ORDER BY sum " + params['order'] + ", w.id ASC"

    if params['index'] or params['page'] > 1:
        query_str += " SKIP "+ str(params['index'] + ((params['page']-1)*params['limit']))
    if params['limit']:
        query_str += " LIMIT {{limit}}"

    # Apply this query to given account only
    accLbl = ""
    if account is not None:
        accLbl = "`%d`:" % account
    query_str = query_str.format(accLbl)
    
    if countResults:
        resp = _query_count(query_str, params)
    else:
        if app.debug:
            print query_str

        tx = neo4j_conn.g_session.create_transaction()
        tx.append(query_str, params)
        results = tx.commit()
        print results

        words = []
        count = -1
        for count,record in enumerate(results[0]):
            word = {
                'word':  record[0],
                'count': record[1]
                }

            words.append(word)

        resp = {}
        resp['_count'] = count+1
        resp['_params'] = params
        resp['_query'] = query_str
        resp['word'] = words

    t1 = time.time()
    resp['_query_time'] = t1-t0

    return resp


def _query_count(query_str, params):
    count_str = query_str[0:query_str.find("RETURN")]
    count_str += "RETURN count(*)"

    if app.debug:
        print count_str

    tx = neo4j_conn.g_session.create_transaction()
    tx.append(count_str, params)
    results = tx.commit()

    resp = {'count': results[0][0][0] }
    resp['_params'] = params
    resp['_query'] = count_str
    return resp


    