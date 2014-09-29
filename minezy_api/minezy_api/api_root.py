from minezy_api import app
from flask import jsonify, request


@app.route('/', methods=['GET'])
def index():
    api_versions = {}
    api_versions['v1'] = 'http://' + request.host + '/1'
    api_versions['v2'] = 'http://' + request.host + '/2'
    return jsonify( { 'api_versions' : api_versions } )

