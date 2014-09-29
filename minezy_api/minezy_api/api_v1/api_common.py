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


def query_params(request):
    query_params = {}

    query_params['index'] = request.args.get('index',default=0,type=int)
    query_params['limit'] = request.args.get('limit',default=0,type=int)
    query_params['start'] = int(request.args.get('start',default=0,type=float))
    query_params['end'] = int(request.args.get('end',default=0,type=float))
    query_params['keyword'] = request.args.get('keyword',default='',type=str)
    query_params['from'] = request.args.getlist('from')
    query_params['to'] = request.args.getlist('to')
    query_params['cc'] = request.args.getlist('cc')
    query_params['bcc'] = request.args.getlist('bcc')
    query_params['year'] = request.args.get('year',default=0,type=int)
    query_params['month'] = request.args.get('month',default=0,type=int)
    query_params['day'] = request.args.get('day',default=0,type=int)

    query_params['page'] = request.args.get('page',default=1,type=int)
    if query_params['page'] < 1:
        query_params['page'] = 1
        
    field = request.args.get('field',default='SENT|TO',type=str).upper()
    count = request.args.get('count',default=field,type=str).upper()
    count = count.replace('|','+').replace(' ','+')
    query_params['count'] = count.split('+')

    query_params['order'] = request.args.get('order',default='DESC',type=str).upper()
    if not (query_params['order'] == 'ASC' or query_params['order'] == 'DESC'):
        query_params['order'] = 'DESC' 
    
    return query_params

