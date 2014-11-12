from flask import Flask
from flask.ext.cors import CORS
from flask.ext.cache import Cache

app = Flask(__name__)
cors = CORS(app)
app.cache = Cache(app,config={'CACHE_TYPE': 'simple'})

import api_root
import api_v1
import api_v2
