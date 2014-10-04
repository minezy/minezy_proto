import time
import calendar
from datetime import date, timedelta
from minezy_api import neo4j_conn
from query_common import prepare_date_range

def query_dates(params, countResults=False):

    t0 = time.time()
    
    bYear = True
    bMonth = False
    bDay = False
    ymd_rel = 'YEAR'
    for cnt in params['count']:
        if cnt == 'MONTH':
            ymd_rel = 'MONTH'
            bMonth = True
        elif cnt == 'DAY':
            ymd_rel = 'DAY'
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
            query_str = "MATCH (cL:Contact)-[rL:"+relL+"]-(e:Email)-[rR:"+relR+"]-(cR:Contact) "
            query_str += "WHERE cL.email IN {left} AND cR.email IN {right} "
            query_str += "AND (type(rL)='SENT' OR type(rR)='SENT') "
            
            if len(params['observer']):
                query_str += "WITH e MATCH (e)--(cO:Contact) WHERE cO.email IN {observer} "
            
        elif len(params['left']):
            query_str = "MATCH (cL:Contact)-[rL:"+relL+"]-(e:Email)-[rR:"+relR+"]-(cR:Contact) "
            query_str += "WHERE cL.email IN {left} "
            query_str += "AND (type(rL)='SENT' OR type(rR)='SENT') "
            
        else:
            query_str = "MATCH (cL:Contact)-[rL:"+relL+"]-(e:Email)-[rR:"+relR+"]-(cR:Contact) WHERE m.email IN {right} "
            query_str += "WHERE cR.email IN {right} "
            query_str += "AND (type(rL)='SENT' OR type(rR)='SENT') "

        query_str += "WITH e MATCH (e)-[:YEAR]->(y),(e)-[:MONTH]->(m),(e)-[:DAY]->(d) "
        params['ymd'] = prepare_date_range(params)[0]
        if len(params['ymd']):
            query_str += "WHERE (y.num IN {ymd} OR m.num IN {ymd} OR d.num IN {ymd}) "

        if bDay:
            query_str += "WITH d.num%100 as day, m.num%100 as month, y.num as year, "
        elif bMonth:
            query_str += "WITH m.num%100 as month, y.num as year, "
        else:
            query_str += "WITH y.num as year, "

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
        
    else:
        ymd_label = ymd_rel.title()
        
        if params['start'] or params['end']:
            startdate = date.fromtimestamp(params['start'])
            enddate = date.fromtimestamp(params['end'])
        
            ymd = []
            delta = enddate - startdate
            for i in range(delta.days+1):
                d = startdate + timedelta(days=i)
                if bDay:
                    ymd.append(d.year*10000 + d.month*100 + d.day)
                elif bMonth:
                    ymd.append(d.year*100 + d.month)
                else:
                    ymd.append(d.year)
            params['ymd'] = list(set(ymd))
            
            query_str = "MATCH (d:"+ymd_label+") WHERE d.num IN {ymd} "
        else:
            query_str = "MATCH (d:"+ymd_label+") "
        
        query_str += "WITH d ORDER BY d.num " + params['order']
        
        if params['index'] or params['page'] > 1:
            query_str += " SKIP "+ str(params['index'] + ((params['page']-1)*params['limit']))
        if params['limit']:
            query_str += " LIMIT {limit}"
        
        query_str += " RETURN " 
        if bDay:
            query_str += "(d.num%100) as day, (d.num/100)%100 as month, (d.num/100)/100 as year"
        elif bMonth:
            query_str += "(d.num)%100 as month, (d.num/100) as year"
        else:
            query_str += "d.num as year"
        query_str += ", LENGTH((d)<-[]-(:Email)) as count "

            
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
            entry = {
                '_ord': ordinal + count,
                'count': record['count'],
                'year': record['year']
                } 
            
            if bMonth:
                entry['month'] = record['month']
            if bDay:
                entry['day'] = record['day']
            
            dates.append(entry)
    
        resp = {}
        resp['_count'] = count+1
        resp['_params'] = params
        resp['_query'] = query_str
        resp['dates'] = dates

    t1 = time.time()
    resp['_query_time'] = t1-t0
    
    return resp

def query_dates_range(params):

    t0 = time.time()
    
    resp = {}
    #resp['_count'] = count+1
    #resp['_params'] = params
    #resp['_query'] = query_str
    #resp['dates'] = dates

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


