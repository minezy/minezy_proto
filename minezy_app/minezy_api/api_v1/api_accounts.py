from minezy_api import app
from api_common import support_jsonp, query_params, query_cache_key
from query_accounts import query_accounts, query_accounts_create, query_accounts_delete
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
def accounts_create(account):
    params = query_params(request)
    resp = query_accounts_create(params, account)
    return jsonify( { 'accounts' : resp } )


@app.route('/1/accounts/delete/<int:accountId>', methods=['PUT', 'GET'])
@support_jsonp
def accounts_delete(accountId):
    params = query_params(request)
    resp = query_accounts_delete(params, accountId)
    return jsonify( { 'accounts' : resp } )
