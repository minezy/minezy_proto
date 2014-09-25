import sys
from minezy_api import app
from flask import jsonify, request

@app.route('/2/', methods=['GET'])
def get_api_v2():
    apis_v1 = [
        {
            'api': '/2/load_imap/<server>/<login>/<passwd>',
            'description': 'load email from account into database'
        },

        # Contacts
        {
            'api': '/2/contacts/',
            'description': 'List contacts',
            'href': 'http://' + request.host + '/2/contacts?limit=10'
        },
        {
            'api': '/2/emails/',
            'description': 'List emails',
            'href': 'http://' + request.host + '/2/emails?limit=10'
        },
        {
            'api': '/2/dates/',
            'description': 'List dates emails occurred',
            'href': 'http://' + request.host + '/2/dates?limit=10'
        },
        {
            'api': '/2/cliques',
            'description': 'List cliques of contacts',
            'href': 'http://' + request.host + '/2/cliques?limit=10'
        },
        {
            'api': '/2/traits/<email>/',
            'description': 'Get actor details'
        }
    ]
    return jsonify( { 'apis' : apis_v1 } )


