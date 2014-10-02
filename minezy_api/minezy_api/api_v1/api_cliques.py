from minezy_api import app
from minezy_api.api_v1.api_common import support_jsonp, query_params
from minezy_api.api_v1.query_cliques import query_cliques
from flask import jsonify, request


@app.route('/1/cliques/', methods=['GET'])
@support_jsonp
def cliques():
    params = query_params(request)
    resp = query_cliques(params)
    return jsonify( { 'cliques' : resp } )

@app.route('/1/cliques/count/', methods=['GET'])
@support_jsonp
def cliques_count():
    params = query_params(request)
    resp = query_cliques(params, countResults=True)
    return jsonify( { 'cliques' : resp } )

