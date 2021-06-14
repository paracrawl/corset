import os
basedir = os.path.abspath(os.path.dirname(__file__))


# pylint: disable=too-few-public-methods
class Config:
    # Some paths to save stuff
    BASEDIR = basedir
    APP_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    DATA_FOLDER = os.path.join(APP_FOLDER, 'data')

    # Location of the database, for now, a sqlite3 file
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(DATA_FOLDER, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'development key'  # change by your own
    DEBUG = False

    INFIX = '.min' if os.environ.get('DEBUG') is None else ''

    SOURCE_LANGS = os.environ.get('SOURCE_LANGS').split('|') if os.environ.get('SOURCE_LANGS') else ['en', 'es']

    API_URL = os.environ.get('API_URL')

    # Authentication settings. Set ENABLE_NEW_LOGINS to True if you want to log in for the first time
    USER_LOGIN_ENABLED = True
    ENABLE_NEW_LOGINS = True
    BANNED_USERS = []
    ADMINS = []
    OAUTHLIB_INSECURE_TRANSPORT = True # True also behind firewall,  False -> require HTTPS
    GOOGLE_USER_DATA_URL = '/oauth2/v1/userinfo'

    # These work!
    GOOGLE_OAUTH_CLIENT_ID = 'YOURCLIENTID'
    GOOGLE_OAUTH_CLIENT_SECRET = 'YOURCLIENTSECRET'
    
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_PROTECTION = 'strong'
