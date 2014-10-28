from minezy_api import app
from api_common import support_jsonp, query_params
from query_emails import query_emails, query_emails_meta, query_emails_body
from flask import jsonify, request


@app.route('/1/emails/', methods=['GET'])
@app.route('/1/<int:account>/emails/', methods=['GET'])
@support_jsonp
def emails(account=None):
    params = query_params(request)
    resp = query_emails(account, params)
    return jsonify( { 'emails' : resp } )


@app.route('/1/emails/meta/', methods=['GET'])
@app.route('/1/<int:account>/emails/meta/', methods=['GET'])
@support_jsonp
def emails_meta(account=None):
    params = query_params(request)
    resp = query_emails_meta(account, params)
    return jsonify( { 'emails' : resp } )


@app.route('/1/emails/body/', methods=['GET'])
@app.route('/1/<int:account>/emails/body/', methods=['GET'])
@support_jsonp
def emails_body(account=None):
    params = query_params(request)
    resp = query_emails_body(account, params)
    return jsonify( { 'emails' : resp } )


@app.route('/1/emails/count/', methods=['GET'])
@app.route('/1/<int:account>/emails/count/', methods=['GET'])
@support_jsonp
def emails_count(account=None):
    params = query_params(request)
    resp = query_emails(account, params, countResults=True)
    return jsonify( { 'emails' : resp } )
    
    
