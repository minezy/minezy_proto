from minezy_api import app
from minezy_api.api_v1.api_common import support_jsonp, query_params
from minezy_api.api_v1.query_dates import query_dates
from flask import jsonify, request
from __builtin__ import str


@app.route('/1/dates/', methods=['GET'])
@support_jsonp
def dates():
    params = query_params(request)
    resp = query_dates(params)
    return jsonify( { 'dates' : resp } )

@app.route('/1/dates/count/', methods=['GET'])
@support_jsonp
def dates_count():
    params = query_params(request)
    resp = query_dates(params, countResults=True)
    return jsonify( { 'dates' : resp } )
    
    