from minezy_api import app
from flask import jsonify, request

@app.route('/1/', methods=['GET'])
@app.route('/v1/', methods=['GET'])
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
            'api': '/1/names/',
            'description': 'List names used in emails',
            'href': 'http://' + request.host + '/1/names?limit=10'
        },
        {
            'api': '/1/cliques/',
            'description': 'List cliques contact(s) are in',
            'href': 'http://' + request.host + '/1/cliques?limit=10'
        },
        {
            'api': '/1/observers/',
            'description': 'List of contacts that observe conversations between contacts',
            'href': 'http://' + request.host + '/1/observers?limit=10'
        },
        {
            'api': '/1/words/',
            'description': 'List common words',
            'href': 'http://' + request.host + '/1/cliques?limit=10'
        }
    ]
    return jsonify( { 'apis' : apis_v1 } )


@app.route('/1/new_account', methods=['GET'])
def new_account():
    return jsonify( { 'account' : 100 } )

@app.route('/1/new_account/progress', methods=['GET'])
def new_account_progress():
    return jsonify( { 'progress' : 100 } )


