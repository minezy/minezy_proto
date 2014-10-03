import time
from minezy_api import neo4j_conn


def query_dates(params, countResults=False):

    t0 = time.time()
    
    bYear = True
    bMonth = False
    bDay = False
    for cnt in params['count']:
        if cnt == 'MONTH':
            bMonth = True
        elif cnt == 'DAY':
            bMonth = True
            bDay = True
    
    if params['rel'] == 'SENDER':
        relL = 'SENT'
        relR = 'TO|CC|BCC'
    elif params['rel'] == 'RECEIVER':
        relL = 'TO|CC|BCC'
        relR = 'SENT'
    else:
        relL = 'SENT|TO|CC|BCC'
        relR = 'SENT|TO|CC|BCC'
            
    rels = ''
    #if len(params['count']):
        #rels = ':' + '|'.join(params['count'])
    
    if len(params['left']) or len(params['right']):
        
        if len(params['left']) and len(params['right']):
            query_str = "MATCH (m:Contact)-[rL:"+relL+"]-(e:Email)-[rR:"+relR+"]-(n:Contact) "
            query_str += "WHERE m.email IN {left} AND n.email IN {right} "
            query_str += "AND (type(rL)='SENT' OR  type(rR)='SENT') "
            
            if len(params['observer']):
                query_str += "WITH e MATCH (e)--(n:Contact) WHERE n.email IN {observer} "
            
        elif len(params['left']):
            query_str = "MATCH (m:Contact)-[rL:"+relL+"]-(e:Email)-[rR:"+relR+"]-(n:Contact) WHERE m.email IN {left} "
            query_str += "AND (type(rL)='SENT' OR  type(rR)='SENT') "
            
        else:
            query_str = "MATCH (m:Contact)-[rL:"+relL+"]-(e:Email)-[rR:"+relR+"]-(n:Contact) WHERE m.email IN {right} "
            query_str += "AND (type(rL)='SENT' OR  type(rR)='SENT') "

        query_str += "AND has(e.timestamp) "
        
    else:
        query_str = "MATCH (e:Email) WHERE has(e.timestamp) "
    
    if params['year']:
        query_str += "AND e.year={year} "
    if params['month']:
        query_str += "AND e.month={month} "
    if params['day']:
        query_str += "AND e.day={day} "

    if params['start']:
        query_str += "AND e.timestamp >= {start} "
    if params['end']:
        query_str += "AND e.timestamp <= {end} "
        
    if bYear:
        query_str += "WITH e.year AS year, "
    if bMonth:
        query_str += "e.month AS month, "
    if bDay:
        query_str += "e.day AS day, "
            
    query_str += "count(distinct(e)) AS count RETURN "

    if bYear:
        query_str += "year,"
    if bMonth:
        query_str += "month,"
    if bDay:
        query_str += "day,"

    query_str += "count ORDER BY "
    
    if bYear:
        query_str += "year " + params['order']
    if bMonth:
        query_str += ", month " + params['order']
    if bDay:
        query_str += ", day " + params['order']
        
    if params['index'] or params['page'] > 1:
        query_str += " SKIP "+ str(params['index'] + ((params['page']-1)*params['limit']))
    if params['limit']:
        query_str += " LIMIT {limit}"
    
    if countResults:
        resp = _query_count(query_str, params)
    else:
        print query_str
        
        tx = neo4j_conn.g_session.create_transaction()
        tx.append(query_str, params)
        results = tx.commit()
        
        dates = []
        count = -1
        ordinal = 1 + params['index'] + (params['page']-1)*params['limit']
        for count,record in enumerate(results[0]):
            date = {
                '_ord': ordinal + count,
                'count': record['count'],
                'year': record['year']
                } 
            
            if bMonth:
                date['month'] = record['month']
            if bDay:
                date['day'] = record['day']
            
            dates.append(date)
    
        resp = {}
        resp['_count'] = count+1
        resp['_params'] = params
        resp['_query'] = query_str
        resp['dates'] = dates

    t1 = time.time()
    resp['_query_time'] = t1-t0
    
    return resp


def _query_count(query_str, params):
    count_str = query_str[0:query_str.find("RETURN")]
    count_str += "RETURN count(*) AS count"
    
    print count_str
    
    tx = neo4j_conn.g_session.create_transaction()
    tx.append(count_str, params)
    results = tx.commit()
    
    resp = {'count': results[0][0]['count'] }
    resp['_params'] = params
    resp['_query'] = count_str
    return resp


