import sys
import json
from py2neo import neo4j, node, rel
import neo4j_conn


def query_actors(query_params, countResults=False):

    index = query_params.get('index', 0)
    limit = query_params.get('limit', 0)
    fromActors = query_params.get('from', [])
    toActors = query_params.get('to', [])

    order = query_params.get('order', 'DESC')
    if not order.lower() == 'asc':
        order = 'DESC' 

    if len(fromActors):
        query_str = "MATCH (n:Contact)-[:Sent]->()-[r:TO|CC|BCC]->(m:Contact) WHERE "
        for i, actor in enumerate(fromActors):
            if i > 0:
                query_str += "OR "
            query_str += "n.email='"+actor+"' "
        query_str += " with m,count(r) as rc RETURN m.name,m.email,rc ORDER BY rc " + order
    else:
        query_str = "MATCH (n:Contact)-[r]-() WITH n,count(r) as rc RETURN n.name,n.email,rc ORDER BY rc " + order
    if index:
        query_str += " SKIP "+ str(index)
    if limit:
        query_str += " LIMIT "+ str(limit)

    if countResults:
        resp = _query_count(query_str)
    else:
        query = neo4j.CypherQuery(neo4j_conn.g_graph, query_str)
    
        actors = []
        for count,record in enumerate(query.stream()):
            actor = { 
                'name':  record[0],
                'email': record[1] 
                } 
            
            actors.append(actor)
    
        resp = {}
        resp['_count'] = count+1
        if index or limit:
            resp['_range'] = { 'index' : index, 'limit' : limit }
        resp['actor'] = actors

    if len(fromActors):
        resp['_from'] = fromActors
    if len(toActors):
        resp['_to'] = toActors
    
    return resp


def _query_count(query_str):
    count_str = query_str[0:query_str.find("RETURN")]
    count_str += "RETURN count(*)"
    
    query = neo4j.CypherQuery(neo4j_conn.g_graph, count_str)
    results = query.execute()

    resp = {'_count': results[0][0] }
    return resp
    