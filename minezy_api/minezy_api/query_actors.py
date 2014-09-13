import sys
import json
from py2neo import neo4j, node, rel
import neo4j_conn


def query_actors(query_params, countResults=False):

    index = query_params.get('index', 0)
    limit = query_params.get('limit', 0)
    order = query_params.get('order', 'DESC').upper()
    field = query_params.get('field', 'TO|CC|BCC').upper()
    fromActors = query_params.get('from', [])
    toActors = query_params.get('to', [])
    
    if len(fromActors):
        query_str = "MATCH (n:Contact)-[:Sent]->()-[r:"+field+"]->(m:Contact) WHERE "
        for i, actor in enumerate(fromActors):
            if i > 0:
                query_str += "OR "
            query_str += "n.email='"+actor+"' "
        query_str += " with m,count(r) as rc RETURN m.name,m.email,rc ORDER BY rc " + order
    elif len(toActors):
        query_str = "MATCH (n:Contact)-[r:Sent]->()-[:"+field+"]->(m:Contact) WHERE "
        for i, actor in enumerate(toActors):
            if i > 0:
                query_str += "OR "
            query_str += "m.email='"+actor+"' "
        query_str += " with n,count(r) as rc RETURN n.name,n.email,rc ORDER BY rc " + order
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
        count = -1
        for count,record in enumerate(query.stream()):
            actor = { 
                'name':  record[0],
                'email': record[1] 
                } 
            
            actors.append(actor)
    
        resp = {}
        resp['_count'] = count+1
        resp['_field'] = field
        resp['_query'] = query_str
        if index or limit:
            resp['_range'] = { 'index' : index, 'limit' : limit }
        if len(actors):
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
    