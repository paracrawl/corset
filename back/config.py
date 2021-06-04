import os
from sqlalchemy import create_engine
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    '''
    Configuration needed in the `back` module.
    '''
    DPDB_URI = os.environ.get('DATABASE_URL')
    SOLR_URI = os.environ.get('SOLR_URL')
    SOLR_USR = os.environ.get('SOLR_USR')
    SOLR_PWD = os.environ.get('SOLR_PWD')
    db = create_engine(DPDB_URI)

    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_WORKER_CONCURRENCY = 4

    BASEDIR = basedir
    ROOT_DIR = os.path.join(BASEDIR, "..")

    APP_FOLDER = os.path.abspath(os.path.join(os.path.dirname( __file__ ), ''))
    DATA_FOLDER = os.path.join(APP_FOLDER, "data")
    SCRIPTS_FOLDER = os.path.join(ROOT_DIR, 'scripts')
    CORSETS_FOLDER = os.path.join(DATA_FOLDER, "corsets")

    CORSET_SIZE = {
        'small': 10000,
        'medium': 100000,
        'large': 1000000
    }

    CORPORA_LINE_LIMIT = 10000
    CORPORA_SAMPLE_SIZE = 5000
