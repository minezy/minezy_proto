import sys
from flask import Flask
from flask.ext.cors import CORS
from flask.ext.cache import Cache

app = Flask(__name__)
cors = CORS(app)

try:
    sys.stdout.write("Flask-Cache 'memcached'... ")
    app.cache = Cache(app,config={'CACHE_TYPE': 'memcached', 'CACHE_MEMCACHED_SERVERS': ['127.0.0.1:11211']})
    sys.stdout.write("OK\n")
except:
    sys.stdout.write("Failed\n")
    sys.stdout.write("Flask-Cache 'simple'... ")
    app.cache = Cache(app,config={'CACHE_TYPE': 'simple'})
    sys.stdout.write("OK\n")
    pass

import api_root
import api_v1
import api_v2
