from minezy_api import app
from api_common import support_jsonp, query_params
from query_dates import query_dates, query_dates_range
from flask import jsonify, request
from flask.ext.cache import Cache


@app.route('/1/dates/', methods=['GET'])
@app.route('/1/<int:account>/dates/', methods=['GET'])
@app.cache.cached(timeout=300) 
@support_jsonp
def dates(account=None):
    params = query_params(request)
    resp = query_dates(account, params)
    return jsonify( { 'dates' : resp } )


@app.route('/1/dates/range/', methods=['GET'])
@app.route('/1/<int:account>/dates/range/', methods=['GET'])
@app.cache.cached(timeout=300) 
@support_jsonp
def dates_range(account=None):
    params = query_params(request)
    resp = query_dates_range(account, params)
    return jsonify( { 'dates' : resp } )


@app.route('/1/dates/count/', methods=['GET'])
@app.route('/1/<int:account>/dates/count/', methods=['GET'])
@app.cache.cached(timeout=300) 
@support_jsonp
def dates_count(account=None):
    params = query_params(request)
    resp = query_dates(account, params, countResults=True)
    return jsonify( { 'dates' : resp } )

