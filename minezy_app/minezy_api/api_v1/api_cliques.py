from minezy_api import app
from api_common import support_jsonp, query_params
from query_cliques import query_cliques
from flask import jsonify, request
from flask.ext.cache import Cache


@app.route('/1/cliques/', methods=['GET'])
@app.cache.cached(timeout=300) 
@support_jsonp
def cliques():
    params = query_params(request)
    resp = query_cliques(params)
    return jsonify( { 'cliques' : resp } )

@app.route('/1/cliques/count/', methods=['GET'])
@app.cache.cached(timeout=300) 
@support_jsonp
def cliques_count():
    params = query_params(request)
    resp = query_cliques(params, countResults=True)
    return jsonify( { 'cliques' : resp } )

