from minezy_api import app
from api_common import support_jsonp, query_params, query_cache_key
from query_words import query_words
from flask import jsonify, request, redirect, url_for
from flask.ext.cache import Cache

@app.route('/1/words/', methods=['GET'])
@app.route('/1/<int:account>/words/', methods=['GET'])
@app.cache.cached(key_prefix=query_cache_key) 
@support_jsonp
def words(account=None):
    params = query_params(request)
    resp = query_words(account, params)
    return jsonify( { 'words' : resp } )

@app.route('/1/words/count/', methods=['GET'])
@app.route('/1/<int:account>/words/count/', methods=['GET'])
@app.cache.cached(key_prefix=query_cache_key) 
@support_jsonp
def words_count(account=None):
    params = query_params(request)
    resp = query_words(account, params, countResults=True)
    return jsonify( { 'words' : resp } )
    
