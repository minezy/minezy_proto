import sys
from flask import Flask
from flask.ext.cors import CORS
from flask.ext.cache import Cache

app = Flask(__name__)
cors = CORS(app)

try:
    sys.stdout.write("Connect to Memcached... ")
    app.cache = Cache(app,config={'CACHE_TYPE': 'memcached'})
    sys.stdout.write("OK\n")
except:
    sys.stdout.write("Failed\n")
    sys.stdout.write("Using 'Simple' Flask-Cache.\n")
    app.cache = Cache(app,config={'CACHE_TYPE': 'simple'})
    pass

import api_root
import api_v1
import api_v2
