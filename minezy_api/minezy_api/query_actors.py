import sys
import json
import time
from py2neo import cypher, node, rel
import neo4j_conn


def query_actors(query_params, countResults=False):

    t0 = time.time()
    
    index = query_params.get('index', 0)
    limit = query_params.get('limit', 0)
    page = query_params.get('page', 1)
    start = query_params.get('start', 0)
    end = query_params.get('end', 0)
    order = query_params.get('order', 'DESC').upper()
    field = query_params.get('field', 'TO|CC|BCC').upper()
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
    if len(fromActors):
        params['from'] = fromActors
    if len(toActors):
        params['to'] = toActors
    
    bWhere = True
    if len(fromActors):
        query_str = "MATCH (m:Actor)-[:Sent]->(e)-[r:"+field+"]->(n:Actor) WHERE ("
        for i, actor in enumerate(fromActors):
            if i > 0:
                query_str += " OR "
            query_str += "m.email='"+actor+"'"
        query_str += ") "
    elif len(toActors):
        query_str = "MATCH (n:Actor)-[r:Sent]->(e)-[:"+field+"]->(m:Actor) WHERE ("
        for i, actor in enumerate(toActors):
            if i > 0:
                query_str += " OR "
            query_str += "m.email='"+actor+"'"
        query_str += ") "

    else:
        bWhere = False
        query_str = "MATCH (n:Actor)-[r]-(e) "
        
    if start or end:
        if not bWhere:
            query_str += "WHERE "
        else:
            query_str += "AND "
    if start:
        query_str += "e.timestamp >= {start} "
    if start and end:
        query_str += "AND "
    if end:
        query_str += "e.timestamp <= {end} "
        
    query_str += "WITH n,count(r) AS rc "
    query_str += "RETURN n.name,n.email,rc ORDER BY rc " + order
    
    if index or page > 1:
        query_str += " SKIP "+ str(index + ((page-1)*limit))
    if limit:
        query_str += " LIMIT {limit}"

    if countResults:
        resp = _query_count(query_str, params)
    else:
        tx = neo4j_conn.g_session.create_transaction()
        tx.append(query_str, params)
        results = tx.commit()
    
        actors = []
        count = -1
        for count,record in enumerate(results[0]):
            actor = { 
                'name':  record[0],
                'email': record[1],
                'count': record[2]
                } 
            
            actors.append(actor)
    
        resp = {}
        resp['_count'] = count+1
        resp['_params'] = params
        resp['_query'] = query_str
        if len(actors):
            resp['actor'] = actors

    t1 = time.time()
    resp['_query_time'] = t1-t0
    
    return resp


def _query_count(query_str, params):
    count_str = query_str[0:query_str.find("RETURN")]
    count_str += "RETURN count(*)"
    
    tx = neo4j_conn.g_session.create_transaction()
    tx.append(count_str, params)
    results = tx.commit()
    
    resp = {'count': results[0][0][0] }
    resp['_params'] = params
    resp['_query'] = count_str
    return resp

    