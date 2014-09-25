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

    print "Query received..."
    query_params['index'] = request.args.get('index',default=0,type=int)
    query_params['limit'] = request.args.get('limit',default=0,type=int)
    query_params['start'] = int(request.args.get('start',default=0,type=float))
    query_params['end'] = int(request.args.get('end',default=0,type=float))

    query_params['page'] = request.args.get('page',default=1,type=int)
    if query_params['page'] < 1:
        query_params['page'] = 1
       
    query_params['order'] = request.args.get('order',default='DESC',type=str).upper()
    if not (query_params['order'] == 'ASC' or query_params['order'] == 'DESC'):
        query_params['order'] = 'DESC' 
    
    return query_params

def path_parse(fullpath):
    input = []
    
    components = fullpath.split('/')
    
    prevObj = {}
    for i, comp in enumerate(components):
        comp = comp.lower()
        
        params = {}
        if comp == 'contacts' or comp == 'emails' or comp == 'dates':
            if len(prevObj) > 0:
                input.append(prevObj)
            prevObj = { 'object': comp }
        else:
            kvList = comp.split(';')
            for kv in kvList:
                l = kv.split('=')
                k = None
                v = None
                if len(l) > 0:
                    k = l[0]
                if len(l) > 1:
                    v = l[1]
                params[k] = v
            prevObj['params'] = params

    if len(prevObj) > 0:
        input.append(prevObj)
        
    return input

