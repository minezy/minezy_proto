from flask import Flask
from flask.ext.cors import CORS

app = Flask(__name__)
cors = CORS(app)

import api_root
import api_contacts
import api_emails
import api_dates
