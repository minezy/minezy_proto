import time
from minezy_api import neo4j_conn
from query_common import prepare_date_range, prepare_date_clause


def query_emails(account, params, countResults=False):

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
    
    params['ymd'],bYear,bMonth,bDay = prepare_date_range(params)

    bDateWhere = False
    if len(params['ymd']):
        bDateWhere = True
    
    bWhere = True        
    if len(params['left']) or len(params['right']):
        
        if len(params['left']) and len(params['right']):
            query_str = "MATCH (cL:Contact{0})-[rL:"+relL+"]-(e:Email{0})-[rR:"+relR+"]-(cR:Contact{0})"
            if len(params['observer']):
                query_str += ",(e)--(cO:Contact{0})"
            query_str += " WHERE cL.email IN {{left}} AND cR.email IN {{right}} "
            query_str += "AND (type(rL)='SENT' OR type(rR)='SENT') "
            if len(params['observer']):
                query_str += "AND cO.email IN {{observer}} "
            if bDateWhere:
                query_str += prepare_date_clause(bYear, bMonth, bDay, prefix="WITH e MATCH ")
            
        elif len(params['left']):
            query_str = "MATCH (cL:Contact{0})-[rL:"+relL+"]-(e:Email{0})"
            query_str += prepare_date_clause(bYear, bMonth, bDay, bNode=False, bPath=bDateWhere, bWhere=False, default=' ')
            query_str += "WHERE cL.email IN {{left}} "
            query_str += prepare_date_clause(bYear, bMonth, bDay, bPath=False, bWhere=bDateWhere, bAnd=True)
            
        else:
            query_str = "MATCH (e:Email{0})-[rR:"+relR+"]-(cR:Contact{0})"
            query_str += prepare_date_clause(bYear, bMonth, bDay, bNode=False, bPath=bDateWhere, bWhere=False, default=' ')
            query_str += "WHERE cR.email IN {{right}} "
            query_str += prepare_date_clause(bYear, bMonth, bDay, bPath=False, bWhere=bDateWhere, bAnd=True)
        
    else:
        bWhere = False
        if len(params['ymd']):
            query_str = "MATCH (e:Email{0}),"
            query_str += prepare_date_clause(bYear, bMonth, bDay)
        else:
            query_str = "MATCH (e:Email{0}) "
        
    if params['keyword']:
        if not bWhere:
            query_str += "WHERE "
        else:
            query_str += "AND "
        query_str += "e.subject =~ '(?i).*"+params['keyword']+".*' "
        
    query_str += "RETURN distinct(e) ORDER BY e.timestamp " + params['order']
    
    if params['index'] or params['page'] > 1:
        query_str += " SKIP "+ str(params['index'] + ((params['page']-1)*params['limit']))
    if params['limit']:
        query_str += " LIMIT {{limit}}"

    # Apply this query to given account only
    accLbl = ""
    if account is not None:
        accLbl = ":`%d`" % account
    query_str = query_str.format(accLbl)

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
                'id': record[0]['id'],
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


def query_emails_meta(account, params):

    t0 = time.time()
    
    query_str = "MATCH (e:Email{0})-[r]-(n) WHERE e.id={{id}} WITH e,r,n ORDER BY n.name RETURN e,type(r),collect(n)"

    # Apply this query to given account only
    accLbl = ""
    if account is not None:
        accLbl = ":`%d`" % account
    query_str = query_str.format(accLbl)

    print query_str
    
    tx = neo4j_conn.g_session.create_transaction()
    tx.append(query_str, params)
    results = tx.commit()
    
    email = {}
    email_contacts = {}
    email_thread = {}
    count = -1
    for count,record in enumerate(results[0]):
        r = record[1]
        nc = record[2]
        
        if count == 0:
            e = record[0]
            email = {
                     'id': e['id'],
                     'subject': e['subject'],
                     'link': e['link'],
                     'date':  {
                               "date":  e['date'],
                               "year":  e['year'],
                               "month": e['month'],
                               "day":   e['day'],
                               "utc":   e['timestamp']
                        }
                     }
            
        if r == 'SENT' or r == 'TO' or r == 'CC' or r == 'BCC':
            if r == 'SENT':
                r = 'from'
            r = r.lower()
                
            r_array = []
            for n in nc:
                c = {
                     'email': n['email'],
                     'name':  n['name']
                    } 
                r_array.append(c)
            email_contacts[r] = r_array
            
        else:
            r = r.lower()

            r_array = []
            for n in nc:
                e = {
                     'id': n['id']
                    } 
                r_array.append(e)
            email_thread[r] = r_array
        
    if len(email_contacts):
        email['contacts'] = email_contacts
    if len(email_thread):
        email['thread'] = email_thread
        
    # because there is either 0 or 1 emails returned
    if count > 0:
        count = 0
        
    resp = {}
    resp['_count'] = count+1
    resp['_params'] = params
    resp['_query'] = query_str
    resp['email'] = email

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

    