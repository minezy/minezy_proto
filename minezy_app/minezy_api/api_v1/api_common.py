from flask import request, current_app
from functools import wraps

def support_jsonp(f):
    """Wraps JSONified output for JSONP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False) or request.args.get('jsonp', False)
        if callback:
            content = str(callback) + '(' + str(f().data) + ')'
            return current_app.response_class(content, mimetype='application/json')
        else:
            return f(*args, **kwargs)
    return decorated_function


def query_cache_key(*args, **kwargs):
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    cache_key = (path + args).encode('utf-8')
    return cache_key

            
def query_params(request):
    query_params = {}

    query_params['start'] = int(request.args.get('start',default=0,type=float))
    query_params['end'] = int(request.args.get('end',default=0,type=float))
    
    query_params['year'] = request.args.get('year',default=0,type=int)
    query_params['month'] = request.args.get('month',default=0,type=int)
    query_params['day'] = request.args.get('day',default=0,type=int)

    query_params['keyword'] = request.args.get('keyword',default='',type=str)
    query_params['id'] = request.args.get('id',default='',type=str)
    query_params['name'] = request.args.get('name',type=str)
    query_params['account'] = request.args.get('account',type=str)
    
    query_params['from'] = request.args.getlist('from')
    query_params['to'] = request.args.getlist('to')
    query_params['cc'] = request.args.getlist('cc')
    query_params['bcc'] = request.args.getlist('bcc')

    query_params['left'] = request.args.getlist('left')
    if len(query_params['left']) == 0:
        query_params['left'] = query_params['from']
    query_params['right'] = request.args.getlist('right')
    if len(query_params['right']) == 0:
        query_params['right'] = query_params['to']
    query_params['observer'] = request.args.getlist('observer')
        
    query_params['rel'] = request.args.get('rel',default='',type=str).upper()
    if not (query_params['rel'] == 'SENDER' or query_params['rel'] == 'RECEIVER'):
        query_params['rel'] = 'ANY' 

    query_params['index'] = request.args.get('index',default=0,type=int)
    query_params['limit'] = request.args.get('limit',default=0,type=int)
    query_params['page'] = request.args.get('page',default=1,type=int)
    if query_params['page'] < 1:
        query_params['page'] = 1
        
    field = request.args.get('field',default='SENT|CC|BCC|TO',type=str).upper()
    count = request.args.get('count',default=field,type=str).upper()
    count = count.replace('|','+').replace(' ','+')
    query_params['count'] = count.split('+')

    query_params['order'] = request.args.get('order',default='DESC',type=str).upper()
    if not (query_params['order'] == 'ASC' or query_params['order'] == 'DESC'):
        query_params['order'] = 'DESC' 

    query_params['word'] = request.args.getlist('word')
    
    return query_params

