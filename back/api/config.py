import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # Some paths to save stuff
    BASEDIR = basedir
    APP_FOLDER = os.path.abspath(os.path.join(os.path.dirname( __file__ ), ''))
    DATA_FOLDER = os.path.join(APP_FOLDER, "data")
    UPLOAD_FOLDER = os.path.join(DATA_FOLDER, "uploads")

    # Location of the database, for now, a sqlite3 file
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(DATA_FOLDER, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'development key'  # change by your own
    AUTH_TOKEN_EXPIRATION = os.environ.get('AUTH_TOKEN_EXPIRATION') or 600
    DEBUG = False

    CORS_SUPPORTS_CREDENTIALS = True
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS').split('|')

    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
