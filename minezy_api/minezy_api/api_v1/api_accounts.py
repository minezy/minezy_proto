from minezy_api import app
from api_common import support_jsonp, query_params
from query_accounts import query_accounts, query_accounts_create
from flask import jsonify, request


@app.route('/1/accounts/', methods=['GET'])
@support_jsonp
def accounts():
    params = query_params(request)
    resp = query_accounts(params)
    return jsonify( { 'accounts' : resp } )


@app.route('/1/accounts/count/', methods=['GET'])
@support_jsonp
def accounts_count():
    params = query_params(request)
    resp = query_accounts(params, True)
    return jsonify( { 'accounts' : resp } )


@app.route('/1/accounts/create/<account>', methods=['PUT', 'GET'])
@support_jsonp
def accounts_create(name):
    params = query_params(request)
    resp = query_accounts_create(params, account)
    return jsonify( { 'accounts' : resp } )


@app.route('/1/accounts/delete/<id>', methods=['PUT', 'GET'])
@support_jsonp
def accounts_delete(id):
    params = query_params(request)
    resp = query_accounts_delete(params, id)
    return jsonify( { 'accounts' : resp } )
