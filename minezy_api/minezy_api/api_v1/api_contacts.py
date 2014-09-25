from minezy_api import app
from minezy_api.api_v1.api_common import support_jsonp, query_params
from minezy_api.api_v1.query_contacts import query_contacts
from flask import jsonify, request, redirect, url_for
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
    

@app.route('/1/actors/', methods=['GET'])
@support_jsonp
def actors_deprecated():
    return redirect(url_for('contacts', **request.args))

@app.route('/1/actors/count/', methods=['GET'])
@support_jsonp
def actors_count_deprecated():
    return redirect(url_for('contacts_count', **request.args))
