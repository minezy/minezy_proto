from minezy_api import app
from minezy_api.api_v1.api_common import support_jsonp, query_params
from minezy_api.api_v1.query_emails import query_emails, query_emails_meta
from flask import jsonify, request


@app.route('/1/emails/', methods=['GET'])
@support_jsonp
def emails():
    params = query_params(request)
    resp = query_emails(params)
    return jsonify( { 'emails' : resp } )


@app.route('/1/emails/meta/', methods=['GET'])
@support_jsonp
def emails_meta():
    params = query_params(request)
    resp = query_emails_meta(params)
    return jsonify( { 'emails' : resp } )


@app.route('/1/emails/count/', methods=['GET'])
@support_jsonp
def emails_count():
    params = query_params(request)
    resp = query_emails(params, countResults=True)
    return jsonify( { 'emails' : resp } )
    
    
