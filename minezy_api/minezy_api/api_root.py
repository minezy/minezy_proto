import sys
#import api_actors
from minezy_api import app
from flask import jsonify, request


@app.route('/', methods=['GET'])
def index():
    api_versions = [ { 'v1' : 'http://' + request.host + '/1' } ]
    return jsonify( { 'api_versions' : api_versions } )

@app.route('/1/', methods=['GET'])
def get_api_v1():
    apis_v1 = [
        {
            'api': '/1/load_imap/<server>/<login>/<passwd>',
            'description': 'load email from account into database'
        },

        # Contacts
        {
            'api': '/1/actors/',
            'description': 'List actors',
            'href': 'http://' + request.host + '/1/actors?limit=10'
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
            'description': 'List cliques of actors',
            'href': 'http://' + request.host + '/1/cliques?limit=10'
        },
        {
            'api': '/1/traits/<email>/',
            'description': 'Get actor details'
        }
    ]
    return jsonify( { 'apis' : apis_v1 } )


