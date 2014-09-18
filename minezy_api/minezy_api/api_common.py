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
    query_params['start'] = request.args.get('start',default=0,type=int)
    query_params['end'] = request.args.get('end',default=0,type=int)
    query_params['keyword'] = request.args.get('keyword',default='',type=str)
    query_params['from'] = request.args.getlist('from')
    query_params['to'] = request.args.getlist('to')

    query_params['page'] = request.args.get('page',default=1,type=int)
    if query_params['page'] < 1:
        query_params['page'] = 1

    query_params['order'] = request.args.get('order',default='DESC',type=str).upper()
    if not (query_params['order'] == 'ASC' or query_params['order'] == 'DESC'):
        query_params['order'] = 'DESC' 
    
    query_params['field'] = request.args.get('field',default='TO|CC|BCC',type=str).upper()
    if not (query_params['field'] == 'TO' or query_params['field'] == 'CC' or query_params['field'] == 'BCC'):
        query_params['field'] = 'TO|CC|BCC'
        
    return query_params

