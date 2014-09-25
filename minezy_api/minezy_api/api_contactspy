from minezy_api import app
from minezy_api.api_common import support_jsonp, query_params
from minezy_api.query_contacts import query_contacts
from flask import jsonify, request 
from __builtin__ import str



@app.route('/1/contacts/', methods=['GET'])
@support_jsonp
def contacts():
    params = query_params(request)
    resp = query_contacts(params)
    return jsonify( { 'contacts' : resp } )


@app.route('/1/contacts/count/', methods=['GET'])
@support_jsonp
def contacts_count():
    params = query_params(request)
    resp = query_contacts(params, countResults=True)
    return jsonify( { 'contacts' : resp } )
    
