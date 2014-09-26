import sys
import json
import time
from py2neo import cypher, node, rel
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
    
    if len(params['from']) or len(params['to']) or len(params['cc']) or len(params['bcc']):
        if len(params['from']):
            query_str = "MATCH (n:Contact)-[:SENT]->(e:Email) WHERE n.email IN {from} AND has(e.timestamp) "
        else:
            query_str = "MATCH (e:Email) WHERE has(e.timestamp) "
            
        for to in params['to']:
            query_str += "AND (e)-[:TO]->(:Contact {email:'"+to+"'}) "
        for cc in params['cc']:
            query_str += "AND (e)-[:CC]->(:Contact {email:'"+cc+"'}) "
        for bcc in params['bcc']:
            query_str += "AND (e)-[:BCC]->(:Contact {email:'"+bcc+"'}) "
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
        
    query_str += "WITH e.year AS year, "
    
    if bMonth:
        query_str += "e.month AS month, "
    if bDay:
        query_str += "e.day AS day, "
            
    query_str += "count(e) AS count RETURN year,"

    if bMonth:
        query_str += "month,"
    if bDay:
        query_str += "day,"

    query_str += "count ORDER BY year " + params['order']
    
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
    
    tx = neo4j_conn.g_session.create_transaction()
    tx.append(count_str, params)
    results = tx.commit()
    
    resp = {'count': results[0][0]['count'] }
    resp['_params'] = params
    resp['_query'] = count_str
    return resp


