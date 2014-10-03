import time
from minezy_api import neo4j_conn


def query_contacts(params, countResults=False):

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

    bWhere = True
    bWith = False
    query_str = ''
    if len(params['left']) or len(params['right']):
        
        if len(params['left']) and len(params['right']):
            query_str = "MATCH (m:Contact)-[rL:"+relL+"]-(e:Email)-[rR:"+relR+"]-(n:Contact) "
            query_str += "WHERE m.email IN {left} AND n.email IN {right} "
            query_str += "AND (type(rL)='SENT' OR type(rR)='SENT') "
            query_str += "WITH e MATCH (e)--(n:Contact) WHERE NOT (n.email IN {right} OR n.email IN {left}) "
            
        elif len(params['left']):
            query_str = "MATCH (m:Contact)-[rL:"+relL+"]-(e:Email)-[rR:"+relR+"]-(n:Contact) "
            query_str += "WHERE m.email IN {left} "
            query_str += "AND (type(rL)='SENT' OR type(rR)='SENT') "
            
        else:
            query_str = "MATCH (m:Contact)-[rL:"+relL+"]-(e:Email)-[rR:"+relR+"]-(n:Contact) "
            query_str += "WHERE m.email IN {right} "
            query_str += "AND (type(rL)='SENT' OR type(rR)='SENT') "
            
    elif params['start'] or params['end']:
        rels = ''
        if len(params['count']):
            rels = ':' + '|'.join(params['count'])
            
        bWhere = False
        query_str = "MATCH (n:Contact)-[r"+rels+"]-(e:Email) "
        
    else:
        bWhere = False
        bWith = True
        
        count = relL.split('|')
        query_str = "MATCH (n:Contact) "
        if len(params['count']):
            for i,cnt in enumerate(count):
                if i == 0:
                    query_str += "WITH n,"
                else:
                    query_str += "+"
                if cnt == 'SENT':
                    query_str += "n.sent"
                elif cnt == 'TO':
                    query_str += "n.to"
                elif cnt == 'CC':
                    query_str += "n.cc"
                elif cnt == 'BCC':
                    query_str += "n.bcc"
            query_str += " AS count "

    if params['start'] or params['end']:
        if not bWhere:
            query_str += "WHERE "
            bWhere = True
        else:
            query_str += "AND "
        if params['start']:
            query_str += "e.timestamp >= {start} "
        if params['start'] and params['end']:
            query_str += "AND "
        if params['end']:
            query_str += "e.timestamp <= {end} "

    if params['keyword']:
        if not bWhere:
            query_str += "WHERE "
            bWhere = True
        else:
            query_str += "AND "
        query_str += "n.name =~ '(?i).*"+params['keyword']+".*' "

    if not bWith:
        query_str += "WITH n,count(distinct(e)) as count "
        
    query_str += "RETURN n.name,n.email,count ORDER BY count " + params['order'] + ", n.name ASC"

    if params['index'] or params['page'] > 1:
        query_str += " SKIP "+ str(params['index'] + ((params['page']-1)*params['limit']))
    if params['limit']:
        query_str += " LIMIT {limit}"

    if countResults:
        resp = _query_count(query_str, params)
    else:
        # for debugging
        print query_str

        tx = neo4j_conn.g_session.create_transaction()
        tx.append(query_str, params)
        results = tx.commit()

        contacts = []
        count = -1
        for count,record in enumerate(results[0]):
            contact = {
                'name':  record[0],
                'email': record[1],
                'count': record[2]
                }

            contacts.append(contact)

        resp = {}
        resp['_count'] = count+1
        resp['_params'] = params
        resp['_query'] = query_str
        resp['contact'] = contacts

    t1 = time.time()
    resp['_query_time'] = t1-t0

    return resp


def _query_count(query_str, params):
    count_str = query_str[0:query_str.find("RETURN")]
    count_str += "RETURN count(*)"

    # for debugging
    print count_str

    tx = neo4j_conn.g_session.create_transaction()
    tx.append(count_str, params)
    results = tx.commit()

    resp = {'count': results[0][0][0] }
    resp['_params'] = params
    resp['_query'] = count_str
    return resp


