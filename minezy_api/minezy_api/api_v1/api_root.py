import sys
from minezy_api import app
from flask import jsonify, request

@app.route('/1/', methods=['GET'])
def get_api_v1():
    apis_v1 = [
        {
            'api': '/1/load_imap/<server>/<login>/<passwd>',
            'description': 'load email from account into database'
        },

        # Contacts
        {
            'api': '/1/contacts/',
            'description': 'List contacts',
            'href': 'http://' + request.host + '/1/contacts?limit=10'
        },
        {
            'api': '/1/emails/',
            'description': 'List emails',
            'href': 'http://' + request.host + '/1/emails?limit=10'
        },
        {
            'api': '/1/dates/',
            'description': 'List dates emails occurred',
            'href': 'http://' + request.host + '/1/dates?limit=10'
        },
        {
            'api': '/1/cliques',
            'description': 'List cliques of contacts',
            'href': 'http://' + request.host + '/1/cliques?limit=10'
        },
        {
            'api': '/1/traits/<email>/',
            'description': 'Get actor details'
        }
    ]
    return jsonify( { 'apis' : apis_v1 } )


