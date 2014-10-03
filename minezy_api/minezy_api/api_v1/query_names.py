import time
from minezy_api import neo4j_conn


def query_names(params, countResults=False):

    t0 = time.time()
    
    query_str = "MATCH (n:Name)-[r:NAME]-(c:Contact) "
    
    if len(params['from']) or len(params['to']) or len(params['cc']) or len(params['bcc']) or len(params['left']) or len(params['right']):
        query_str += "WHERE " 
        bDid = False
        if len(params['from']):
            query_str += "c.email IN {from} "
        if len(params['to']):
            if not bDid:
                query_str += "OR "
                bDid = True
            query_str += "c.email IN {to} "
        if len(params['cc']):
            if not bDid:
                query_str += "OR "
                bDid = True
            query_str += "c.email IN {cc} "
        if len(params['bcc']):
            if not bDid:
                query_str += "OR "
                bDid = True
            query_str += "c.email IN {bcc} "
        if len(params['left']):
            if not bDid:
                query_str += "OR "
                bDid = True
            query_str += "c.email IN {left} "
        if len(params['right']):
            if not bDid:
                query_str += "OR "
                bDid = True
            query_str += "c.email IN {right} "
        
    query_str += "WITH n,count(r) as count,collect(c.email) as contacts "            
    query_str += "RETURN n.name as name,count,contacts "
    
    if 'USE' in params['count']:
        query_str += "ORDER BY count DESC, name ASC"
    else:  
        query_str += "ORDER BY name ASC"
    
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
        
        names = []
        count = -1
        ordinal = 1 + params['index'] + (params['page']-1)*params['limit']
        for count,record in enumerate(results[0]):
            name = {
                '_ord': ordinal + count,
                'count': record['count'],
                'name': record['name'],
                'contacts': record['contacts']
                } 
            
            names.append(name)
    
        resp = {}
        resp['_count'] = count+1
        resp['_params'] = params
        resp['_query'] = query_str
        resp['names'] = names

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


