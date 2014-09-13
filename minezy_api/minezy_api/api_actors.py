from minezy_api import app
from flask import jsonify, request
from minezy_api.query_actors import query_actors
from __builtin__ import str


@app.route('/1/actors/', methods=['GET'])
def actors():
    query_params = _parse_query_params()
    resp = query_actors(query_params)
    return jsonify( { 'actors' : resp } )


@app.route('/1/actors/count/', methods=['GET'])
def actors_count():
    query_params = _parse_query_params()
    resp = query_actors(query_params, countResults=True)
    return jsonify( { 'actors' : resp } )
    
    
def _parse_query_params():
    query_params = {}

    query_params['index'] = request.args.get('index',default=0,type=int)
    query_params['limit'] = request.args.get('limit',default=0,type=int)
    query_params['order'] = request.args.get('order',default='DESC',type=str)
    query_params['from'] = request.args.getlist('from')
    query_params['to'] = request.args.getlist('to')
        
    return query_params