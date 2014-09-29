from minezy_api import app
from minezy_api.api_v1.api_common import support_jsonp, query_params
from minezy_api.api_v1.query_names import query_names
from flask import jsonify, request


@app.route('/1/names/', methods=['GET'])
@support_jsonp
def names():
    params = query_params(request)
    resp = query_names(params)
    return jsonify( { 'names' : resp } )


@app.route('/1/names/count/', methods=['GET'])
@support_jsonp
def names_count():
    params = query_params(request)
    resp = query_names(params, countResults=True)
    return jsonify( { 'names' : resp } )
    
    
