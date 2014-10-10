from flask import Flask
from flask.ext.cors import CORS

app = Flask(__name__)
cors = CORS(app)

import api_root
import api_v1
import api_v2
