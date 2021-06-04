from flask_restx import Api
from models.user import User

from . import login_manager
from . import app
from back.api.resources.corpora.query import Query
from back.api.resources.corpora.base import Base
from back.api.resources.corsets.corsets import Corsets
from back.api.resources.corsets.highlights import Highlights
from back.api.resources.job import Job
from back.api.resources.search import Search


# This is the user loader. It returns a User object given a user ID
from back.api.resources.history import History


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(social_id=user_id).first()


api = Api(app)

api.add_resource(Search, '/search')
api.add_resource(History, '/search/history')

api.add_resource(Query, '/corpora/query')
api.add_resource(Base, '/corpora/base', '/corpora/base/<int:corpus_id>',
                 '/corpora/base/<int:source_lang>/<int:target_lang>')

api.add_resource(Corsets, '/corsets', '/corsets/<int:query_request_id>')
api.add_resource(Highlights, '/corsets/highlights')

api.add_resource(Job, '/job', '/job/<int:job_id>')
