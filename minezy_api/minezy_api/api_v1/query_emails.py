import time
from minezy_api import neo4j_conn


def query_emails(params, countResults=False):

    t0 = time.time()
    
    if len(params['from']) or len(params['to']) or len(params['cc']) or len(params['bcc']):
        if len(params['from']):
            query_str = "MATCH (n:Contact)-[]-(e:Email) WHERE n.email IN {from} AND has(e.subject) "
        else:
            query_str = "MATCH (e:Email) WHERE has(e.subject) "
            
        for to in params['to']:
            query_str += "AND (e)-[]-(:Contact {email:'"+to+"'}) "
        for cc in params['cc']:
            query_str += "AND (e)-[:CC]->(:Contact {email:'"+cc+"'}) "
        for bcc in params['bcc']:
            query_str += "AND (e)-[:BCC]->(:Contact {email:'"+bcc+"'}) "
    else:
        query_str = "MATCH (e:Email) WHERE has(e.subject) "
        
    if params['start'] or params['end'] or params['keyword']:
        query_str += "AND "
    if params['start']:
        query_str += "e.timestamp >= {start} "
    if params['start'] and params['end']:
        query_str += "AND "
    if params['end']:
        query_str += "e.timestamp <= {end} "
    if params['keyword']:
        if params['start'] or params['end']:
            query_str += "AND "
        query_str += "e.subject =~ '(?i).*"+params['keyword']+".*' "
        
    query_str += "RETURN e ORDER BY e.timestamp " + params['order'] + " "
    
    if params['index'] or params['page'] > 1:
        query_str += "SKIP "+ str(params['index'] + ((params['page']-1)*params['limit']))
    if params['limit']:
        query_str += "LIMIT {limit}"

    if countResults:
        resp = _query_count(query_str, params)
    else:
        print query_str
        
        tx = neo4j_conn.g_session.create_transaction()
        tx.append(query_str, params)
        results = tx.commit()
        
        emails = []
        count = -1
        ordinal = 1 + params['index'] + (params['page']-1)*params['limit']
        for count,record in enumerate(results[0]):
            email = {
                '_ord': ordinal + count,
                'subject': record[0]['subject'],
                'date':  {
                        "date":  record[0]['date'],
                        "year":  record[0]['year'],
                        "month": record[0]['month'],
                        "day":   record[0]['day'],
                        "utc":   record[0]['timestamp']
                          
                    }
                } 
            
            emails.append(email)
    
        resp = {}
        resp['_count'] = count+1
        resp['_params'] = params
        resp['_query'] = query_str
        resp['email'] = emails

    t1 = time.time()
    resp['_query_time'] = t1-t0
    
    return resp


def _query_count(query_str, params):
    count_str = query_str[0:query_str.find("RETURN")]
    count_str += "RETURN count(*)"
    
    print count_str
    
    tx = neo4j_conn.g_session.create_transaction()
    tx.append(count_str, params)
    results = tx.commit()
    
    resp = {'count': results[0][0][0] }
    resp['_params'] = params
    resp['_query'] = count_str
    return resp

    