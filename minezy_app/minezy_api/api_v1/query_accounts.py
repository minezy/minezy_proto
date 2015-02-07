import time
from minezy_api import app
from minezy_api import neo4j_conn
from datetime import datetime


def query_accounts(params, countResults=False):
    t0 = time.time()
    
    query_str = "MATCH (a:Account) "
    
    if params.get('id'):
        query_str += "WHERE a.id = %s " % params['id']
    elif params.get('account'):
        query_str += "WHERE a.account = %s " % params['account']
    elif params.get('name'):
        query_str += "WHERE a.name = '%s' " % params['name']
    elif params.get('keyword'):
        query_str += "WHERE a.name =~ '(?i).*"+params['keyword']+".*' "
        
    query_str += "RETURN a "
    query_str += "ORDER BY a.name " + params['order']
    
    if params['index'] or params['page'] > 1:
        query_str += " SKIP "+ str(params['index'] + ((params['page']-1)*params['limit']))
    if params['limit']:
        query_str += " LIMIT {limit}"
    
    if countResults:
        resp = _query_count(query_str, params)
    else:
        if app.debug:
            print query_str
        
        tx = neo4j_conn.g_session.cypher.begin()
        tx.append(query_str, params)
        results = tx.commit()
        
        accounts = []
        count = -1
        ordinal = 1 + params['index'] + (params['page']-1)*params['limit']
        for count,record in enumerate(results[0]):
            a = record[0]
            account = {
                '_ord': ordinal + count,
                'account': a['account'],
                'id': a['id'],
                'name': a['name'],
                'created': a['created'],
                'modified': a['modified']
                } 
            
            accounts.append(account)
    
        resp = {}
        resp['_count'] = count+1
        resp['_params'] = params
        resp['_query'] = query_str
        resp['account'] = accounts

    t1 = time.time()
    resp['_query_time'] = t1-t0
    
    return resp


def _query_count(query_str, params):
    count_str = query_str[0:query_str.find("RETURN")]
    count_str += "RETURN count(*) AS count"
    
    if app.debug:
        print count_str
    
    tx = neo4j_conn.g_session.cypher.begin()
    tx.append(count_str, params)
    results = tx.commit()
    
    resp = {'count': results[0][0]['count'] }
    resp['_params'] = params
    resp['_query'] = count_str
    return resp



def query_accounts_create(params, account):
    t0 = time.time()

    tx = neo4j_conn.g_session.cypher.begin()

    # Get max id used
    query_str = "MATCH (a:Account) RETURN max(a.id)"
    tx.append(query_str)
    results = tx.execute()
    
    accountId = 100
    for record in results[0]:
        if record[0] is not None:
            accountId = record[0] + 1
    
    tod = datetime.today()
    props = {
             'id': accountId,
             'account' : account,
             'name': params.get('name'),
             'created': str(tod),
             'modified': str(tod)
             }
    
    query_str = "MERGE (a:Account {id:{props}.id}) SET a={props}"
    if app.debug:
        print query_str
    
    tx.append(query_str, { 'props': props } )
    results = tx.commit()
    
    params['id'] = accountId
    resp = query_accounts(params)
    
    t1 = time.time()
    resp['_query_time'] = t1-t0
    return resp;


def query_accounts_delete(params, id):
    t0 = time.time()

    query_str = "MATCH (a:Account) WHERE id = %s " % str(id)
    query_str += " DELETE a"
    if app.debug:
        print query_str
    
    tx = neo4j_conn.g_session.cypher.begin()
    tx.append(query_str)
    tx.commit()
    
    t1 = time.time()
    resp['_query_time'] = t1-t0
    return resp;

