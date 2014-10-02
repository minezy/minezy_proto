from minezy_api import app
from minezy_api.api_v1.api_common import support_jsonp, query_params
from minezy_api.api_v1.query_observers import query_observers
from flask import jsonify, request


@app.route('/1/observers/', methods=['GET'])
@support_jsonp
def observers():
    params = query_params(request)
    resp = query_observers(params)
    return jsonify( { 'observers' : resp } )

@app.route('/1/observers/count/', methods=['GET'])
@support_jsonp
def observers_count():
    params = query_params(request)
    resp = query_observers(params, countResults=True)
    return jsonify( { 'observers' : resp } )

