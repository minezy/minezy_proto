import sys
import json
import time
from py2neo import cypher, node, rel
import neo4j_conn


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
    
    query_str = "MATCH (e:Email) WHERE has(e.timestamp) "
    
    if params['year']:
        query_str += "AND e.year={year} "
    if params['month']:
        query_str += "AND e.month={month} "
    if params['day']:
        query_str += "AND e.day={day} "

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

    query_str += "count ORDER BY year DESC"
    
    if bMonth:
        query_str += ", month ASC"
    if bDay:
        query_str += ", day ASC"
        
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
        if len(dates):
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


