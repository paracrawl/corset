from flask import Flask
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix

from models.database import db

from .config import Config

# We create the app, we load its config and we provide a ProxyFix to make auth work
# with gunicorn (our app server)
from .utils import utils

app = Flask(__name__, static_folder='static', static_url_path='')
app.config.from_object(Config)

# We load the Login Manager and the Database manager
login_manager = LoginManager(app)

# Blueprints
# A blueprint is somehow like a component. It has its own views.py file to manage routes and
# its own templates folder to manage views
# pylint: disable=wrong-import-position
from .blueprints.settings.views import settings_blueprint
from .blueprints.auth.views import auth_blueprint
from .blueprints.search.views import search_blueprint
from .blueprints.query.views import query_blueprint
from .blueprints.dashboard.views import dashboard_blueprint
from .blueprints.admin.views import admin_blueprint

blueprints = [
    ["/auth", auth_blueprint],
    ["/search", search_blueprint],
    ["/query", query_blueprint],
    ["/dashboard", dashboard_blueprint],
    ["/settings", settings_blueprint],
    ["/admin", admin_blueprint]
]

for blueprint in blueprints:
    app.register_blueprint(blueprint[1], url_prefix=blueprint[0])

# We import routes (which define accessible URLs) and models
# (which define database objects)
from . import routes, models

# We create the database tables and we save the changes
app.app_context().push()
db.init_app(app)
db.create_all()
db.session.commit()

app.wsgi_app = ProxyFix(app.wsgi_app)
