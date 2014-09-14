import sys
import json
import time
from py2neo import neo4j, node, rel
import neo4j_conn


def query_emails(query_params, countResults=False):

    t0 = time.time()
    
    index = query_params.get('index', 0)
    limit = query_params.get('limit', 0)
    page = query_params.get('page', 1)
    start = query_params.get('start', 0)
    end = query_params.get('end', 0)
    order = query_params.get('order', 'DESC').upper()
    field = query_params.get('field', 'TO|CC|BCC').upper()
    keyword = query_params.get('keyword')
    fromActors = query_params.get('from', [])
    toActors = query_params.get('to', [])
    
    params = {}
    params['index'] = index
    params['limit'] = limit
    params['page'] = page
    params['order'] = order
    params['field'] = field
    params['start'] = start
    params['end'] = end
    params['keyword'] = keyword
    if len(fromActors):
        params['from'] = fromActors
    if len(toActors):
        params['to'] = toActors
    
    if len(fromActors) or len(toActors):
        query_str = "MATCH (e:Email)-[r:SentBy]->(n:Contact) WHERE "
        if len(fromActors):
            for i, actor in enumerate(fromActors):
                if i > 0:
                    query_str += "OR "
                query_str += "n.email='"+actor+"' "
            query_str += " WITH DISTINCT e "
            
        if len(toActors):
            query_str += "MATCH (e:Email)-[r:"+field+"]->(n:Contact) WHERE "
            for i, actor in enumerate(toActors):
                if i > 0:
                    query_str += "OR "
                query_str += "n.email='"+actor+"' "
            query_str += " WITH DISTINCT e "
    else:
        query_str = "MATCH (e:Email) "
        
    if start or end or keyword:
        query_str += "WHERE "
    if start:
        query_str += "e.timestamp >= {start} "
    if start and end:
        query_str += "AND "
    if end:
        query_str += "e.timestamp <= {end} "
    if keyword:
        if start or end:
            query_str += "AND "
        query_str += "e.subject =~ '(?i).*"+keyword+".*' "
        
    query_str += "RETURN e ORDER BY e.timestamp " + order
    
    if index or page > 1:
        query_str += " SKIP "+ str(index + ((page-1)*limit))
    if limit:
        query_str += " LIMIT {limit}"

    if countResults:
        resp = _query_count(query_str, params)
    else:
        query = neo4j.CypherQuery(neo4j_conn.g_graph, query_str)
    
        emails = []
        count = -1
        ordinal = 1 + index + (page-1)*limit
        for count,record in enumerate(query.stream(index=index, limit=limit, start=start, end=end)):
            email = {
                '_ord': ordinal + count,
                'date':  record[0]['date'],
                'subject': record[0]['subject'],
                'timestamp': record[0]['timestamp']
                } 
            
            emails.append(email)
    
        resp = {}
        resp['_count'] = count+1
        resp['_params'] = params
        resp['_query'] = query_str
        if len(emails):
            resp['email'] = emails

    t1 = time.time()
    resp['_query_time'] = t1-t0
    
    return resp


def _query_count(query_str, params):
    count_str = query_str[0:query_str.find("RETURN")]
    count_str += "RETURN count(*)"
    
    query = neo4j.CypherQuery(neo4j_conn.g_graph, count_str)
    results = query.execute(index=params['index'], limit=params['limit'], start=params['start'], end=params['end'])

    resp = {'count': results[0][0] }
    resp['_params'] = params
    resp['_query'] = count_str
    return resp

    