from minezy_api import app
from flask import jsonify, request
from minezy_api.query_emails import query_emails
from __builtin__ import str


@app.route('/1/emails/', methods=['GET'])
def emails():
    query_params = _parse_query_params()
    resp = query_emails(query_params)
    return jsonify( { 'emails' : resp } )


@app.route('/1/emails/count/', methods=['GET'])
def emails_count():
    query_params = _parse_query_params()
    resp = query_emails(query_params, countResults=True)
    return jsonify( { 'emails' : resp } )
    
    
def _parse_query_params():
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