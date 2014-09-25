import sys
from flask import jsonify, request
from minezy_api import app
from minezy_api.api_v2.api_common import support_jsonp, query_params, path_parse


@app.route('/2/', methods=['GET'])
def get_api_v2():
    apis_v1 = [
        {
            'api': '/2/<object>/[<params>][/<object>/[params]]?globalparams',
            'description': 'Use a path of objects and parameters. Sub-objects utilize the data from the previous object in the path.'
        },

        # Contacts
        {
            'api': '/2/contacts/',
            'description': 'List contacts',
            'href': 'http://' + request.host + '/2/contacts/limit=10'
        },
        {
            'api': '/2/contacts/from=<email>;limit=10',
            'description': 'List contacts receiving emails from email address, limit to 10',
        },
        {
            'api': '/2/emails/',
            'description': 'List emails',
            'href': 'http://' + request.host + '/2/emails/limit=10'
        },
        {
            'api': '/2/dates/',
            'description': 'List dates emails occurred',
            'href': 'http://' + request.host + '/2/dates/limit=10'
        },
        {
            'api': '/2/traits/<email>/',
            'description': 'Get actor details'
        }
    ]
    return jsonify( { 'apis' : apis_v1 } )


@app.route('/2/<path:fullpath>', methods=['GET'])
def query_path(fullpath):
    input = path_parse(fullpath)
    params = query_params(request)
    return jsonify( { 'params' : params, '_fullpath':fullpath, 'input': input } )

