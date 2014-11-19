import time
from datetime import date, timedelta
from minezy_api import app
from minezy_api import neo4j_conn
from query_common import prepare_date_range, prepare_date_clause, prepare_word_clause

def query_dates(account, params, countResults=False):
    t0 = time.time()
    
    bYear = True
    bMonth = False
    bDay = False
    
    if params['rel'] == 'SENDER':
        relL = 'SENT'
        relR = 'TO|CC|BCC'
    elif params['rel'] == 'RECEIVER':
        relL = 'TO|CC|BCC'
        relR = 'SENT'
    else:
        relL = 'SENT|TO|CC|BCC'
        relR = 'SENT|TO|CC|BCC'
            
    params['ymd'],bYear,bMonth,bDay = prepare_date_range(params)
    
    bDateWhere = False
    if len(params['ymd']):
        bDateWhere = True

    if len(params['left']) or len(params['right']):
        
        if len(params['left']) and len(params['right']):
            query_str = "MATCH (cL:{0}Contact)-[rL:"+relL+"]-(e:{0}Email)-[rR:"+relR+"]-(cR:{0}Contact) "
            query_str += "WHERE cL.email IN {{left}} AND cR.email IN {{right}} "
            query_str += "AND (type(rL)='SENT' OR type(rR)='SENT') "
            
            if len(params['observer']):
                query_str += "WITH e MATCH (e)--(cO:{0}Contact) WHERE cO.email IN {{observer}} "

            query_str += prepare_date_clause(bYear,bMonth,bDay,bWhere=bDateWhere,prefix="WITH e MATCH ")
            
        elif len(params['left']):
            query_str = "MATCH (cL:{0}Contact)-[rL:"+relL+"]-(e:{0}Email)"
            query_str += prepare_date_clause(bYear,bMonth,bDay,bNode=False,bWhere=False,default=' ')
            query_str += "WHERE cL.email IN {{left}} "
            #query_str += "AND (type(rL)='SENT' OR type(rR)='SENT') "
            query_str += prepare_date_clause(bYear,bMonth,bDay,bPath=False,bWhere=bDateWhere,bAnd=True)
            
        else:
            query_str = "MATCH (cL:{0}Contact)-[rL:"+relL+"]-(e:{0}Email)"
            query_str += prepare_date_clause(bYear,bMonth,bDay,bNode=False,bWhere=False,default=' ')
            query_str += "WHERE cR.email IN {{right}} "
            #query_str += "AND (type(rL)='SENT' OR type(rR)='SENT') "
            query_str += prepare_date_clause(bYear,bMonth,bDay,bPath=False,bWhere=bDateWhere,bAnd=True)

        if bDay:
            query_str += "WITH (d.num%100) AS day, ((d.num/100)%100) AS month, ((d.num/100)/100) as year, "
        elif bMonth:
            query_str += "WITH (m.num%100) AS month, (m.num/100) AS year, "
        else:
            query_str += "WITH y.num AS year, "

        query_str += "count(distinct(e)) AS count RETURN "
    
        if bYear or bMonth or bDay:
            query_str += "year,"
        if bMonth or bDay:
            query_str += "month,"
        if bDay:
            query_str += "day,"
    
        query_str += "count ORDER BY "
        
        if bYear or bMonth or bDay:
            query_str += "year " + params['order']
        if bMonth or bDay:
            query_str += ",month " + params['order']
        if bDay:
            query_str += ",day " + params['order']
            
        if params['index'] or params['page'] > 1:
            query_str += " SKIP "+ str(params['index'] + ((params['page']-1)*params['limit']))
        if params['limit']:
            query_str += " LIMIT {{limit}}"

    elif len(params['word']):

        query_str = "MATCH "
        query_str += prepare_word_clause(params['word'], bNode=True, bWhere=False)
        query_str += prepare_date_clause(bYear,bMonth,bDay,bNode=False,bWhere=False,default=' ')
        query_str += prepare_word_clause(params['word'], bPath=False, bWhere=True)
        query_str += prepare_date_clause(bYear, bMonth, bDay, bPath=False, bWhere=bDateWhere, bAnd=True)

        if bDay:
            query_str += "WITH (d.num%100) AS day, ((d.num/100)%100) AS month, ((d.num/100)/100) as year, "
        elif bMonth:
            query_str += "WITH (m.num%100) AS month, (m.num/100) AS year, "
        else:
            query_str += "WITH y.num AS year, "

        query_str += "sum(r.count) AS count RETURN "

        if bYear or bMonth or bDay:
            query_str += "year,"
        if bMonth or bDay:
            query_str += "month,"
        if bDay:
            query_str += "day,"
    
        query_str += "count ORDER BY "
        
        if bYear or bMonth or bDay:
            query_str += "year " + params['order']
        if bMonth or bDay:
            query_str += ",month " + params['order']
        if bDay:
            query_str += ",day " + params['order']
            
        if params['index'] or params['page'] > 1:
            query_str += " SKIP "+ str(params['index'] + ((params['page']-1)*params['limit']))
        if params['limit']:
            query_str += " LIMIT {{limit}}"

    else:
        if bDay:
            ymd_label = 'Day'
            ymd_var = 'd'
        elif bMonth:
            ymd_label = 'Month'
            ymd_var = 'm'
        else:
            ymd_label = 'Year'
            ymd_var = 'y'
        
        query_str = "MATCH (%s:%s) " % (ymd_var, ymd_label)
        query_str += prepare_date_clause(bYear,bMonth,bDay,bPath=False,bWhere=bDateWhere)

        query_str += "WITH %s ORDER BY %s.num %s" % (ymd_var, ymd_var, params['order'])
        
        if params['index'] or params['page'] > 1:
            query_str += " SKIP "+ str(params['index'] + ((params['page']-1)*params['limit']))
        if params['limit']:
            query_str += " LIMIT {{limit}}"
        
        query_str += " RETURN " 
        if bDay:
            query_str += "(d.num%100) as day, (d.num/100)%100 as month, (d.num/100)/100 as year"
        elif bMonth:
            query_str += "(m.num)%100 as month, (m.num/100) as year"
        else:
            query_str += "y.num as year"
        query_str += ", LENGTH((%s)<-[]-(:{0}Email)) as count " % ymd_var

    # Apply this query to given account only
    accLbl = ""
    if account is not None:
        accLbl = "`%d`:" % account
    print query_str
    query_str = query_str.format(accLbl)
            
    if countResults:
        resp = _query_count(query_str, params)
    else:
        if app.debug:
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
            
            if bMonth or bDay:
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


def query_dates_range(account, params, countResults=False):

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
    
    bYear = True
    bMonth = True
    bDay = True
    ymd_label = 'Day'
    for cnt in params['count']:
        if cnt == 'MONTH':
            ymd_label = 'Month'
            bMonth = True
            bDay = False
        elif cnt == 'YEAR':
            ymd_label = 'Year'
            bYear = True
            bMonth = False
            bDay = False
        break
    
    if len(params['left']) or len(params['right']):
        
        if len(params['left']) and len(params['right']):
            query_str = "MATCH (cL:{0}Contact)-[rL:"+relL+"]-(e:{0}Email)-[rR:"+relR+"]-(cR:{0}Contact) "
            query_str += "WHERE cL.email IN {{left}} AND cR.email IN {{right}} "
            
        elif len(params['left']):
            query_str = "MATCH (cL:{0}Contact)-[rL:"+relL+"]-(e:{0}Email) "
            query_str += "WHERE cL.email IN {{left}} "
            
        else:
            query_str = "MATCH (e:{0}Email)-[rR:"+relR+"]-(cR:{0}Contact) "
            query_str += "WHERE cR.email IN {{right}} "
    
        query_str += "WITH e MATCH (e)-->(d:"+ymd_label+"{1}) WITH MIN(d.num) AS dMin, MAX(d.num) AS dMax "
    
    else:
        query_str = "MATCH (d:"+ymd_label+"{1}) WITH MIN(d.num) AS dMin, MAX(d.num) AS dMax "
        
    query_str += "RETURN "
    if bDay:
        query_str += "(dMin%100) as day_min, (dMin/100)%100 as month_min, (dMin/100)/100 as year_min, "
        query_str += "(dMax%100) as day_max, (dMax/100)%100 as month_max, (dMax/100)/100 as year_max"
    elif bMonth:
        query_str += "(dMin)%100 as month_min, (dMin/100) as year_min, "
        query_str += "(dMax)%100 as month_max, (dMax/100) as year_max"
    else:
        query_str += "dMin as year_min, "
        query_str += "dMax as year_max"
        
    # Apply this query to given account only
    accLbl0 = ""
    accLbl1 = ""
    if account is not None:
        accLbl0 = "`%d`:" % account
        accLbl1 = ":`%d`" % account
    query_str = query_str.format(accLbl0,accLbl1)
        
    if countResults:
        resp = _query_count(query_str, params)
    else:
        if app.debug:
            print query_str
        
        tx = neo4j_conn.g_session.create_transaction()
        tx.append(query_str, params)
        results = tx.commit()
        
        daterange = {}
        count = -1
        ordinal = 1 + params['index'] + (params['page']-1)*params['limit']
        for count,record in enumerate(results[0]):
            # need to check for None result because min/max return null when not found
            if None in record:
                count = -1 
                break
            
            range_min = {} 
            range_max = {} 
            if bYear:
                range_min['year'] = record['year_min']
                range_max['year'] = record['year_max']
            if bMonth:
                range_min['month'] = record['month_min']
                range_max['month'] = record['month_max']
            if bDay:
                range_min['day'] = record['day_min']
                range_max['day'] = record['day_max']
            
            daterange['_ord'] = ordinal + count
            daterange['first'] = range_min
            daterange['last'] = range_max
    
        resp = {}
        resp['_count'] = count+1
        resp['_params'] = params
        resp['_query'] = query_str
        resp['range'] = daterange

    t1 = time.time()
    resp['_query_time'] = t1-t0
    
    return resp


def _query_count(query_str, params):
    count_str = query_str[0:query_str.find("RETURN")]
    count_str += "RETURN count(*) AS count"
    
    if app.debug:
        print count_str
    
    tx = neo4j_conn.g_session.create_transaction()
    tx.append(count_str, params)
    results = tx.commit()
    
    resp = {'count': results[0][0]['count'] }
    resp['_params'] = params
    resp['_query'] = count_str
    return resp


