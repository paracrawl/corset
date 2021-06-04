from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from models.database import db
from werkzeug.middleware.proxy_fix import ProxyFix

from back.api.config import Config

app = Flask(__name__, static_folder='static', static_url_path='')
app.config.from_object(Config)
app.wsgi_app = ProxyFix(app.wsgi_app)
login_manager = LoginManager(app)
cors = CORS(app)

db.init_app(app)

from . import api

