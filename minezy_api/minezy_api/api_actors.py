from minezy_api import app
from minezy_api.api_common import support_jsonp, query_params
from minezy_api.query_actors import query_actors
from flask import jsonify, request 
from __builtin__ import str


@app.route('/1/actors/', methods=['GET'])
@support_jsonp
def actors():
    params = query_params(request)
    resp = query_actors(params)
    return jsonify( { 'actors' : resp } )


@app.route('/1/actors/count/', methods=['GET'])
@support_jsonp
def actors_count():
    params = query_params(request)
    resp = query_actors(params, countResults=True)
    return jsonify( { 'actors' : resp } )
    
