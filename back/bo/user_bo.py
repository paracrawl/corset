from sqlalchemy import text
from sqlalchemy.sql import not_
from sqlalchemy.orm import sessionmaker

from back import Config, QueryRequests, Statuses, Users
from back.bo.langs_bo import LangsBO

from back.utils import *

class UserBO:
    Session = sessionmaker(Config.db)
    session = Session()

    def get_pending_tasks(self, user_id):
        try:
            query_requests = self.session.query(QueryRequests).filter_by(owner=user_id)\
                .filter(not_(QueryRequests.status_rel.has(Statuses.status == 'done'))).all()
            pending_requests = query_requests
            ret = pending_requests
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_pending_tasks.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None

    def get_tasks(self, user_id):
        try:
            query_requests = self.session.query(QueryRequests)\
                                .filter_by(owner=user_id)\
                                .order_by(text(QueryRequests.__tablename__+".creation_date desc")).all()

            langs_bo = LangsBO()
            pending_requests = []
            for request in query_requests:
                request = request.to_dto()
                request.owner = request.owner.to_dto()
                request.status = request.status.to_dto()
                request.base_corpus = request.base_corpus.to_dto()
                request.base_corpus.source_lang = langs_bo.get_lang(request.base_corpus.source_lang)
                request.base_corpus.target_lang = langs_bo.get_lang(request.base_corpus.target_lang)
                request.query_corpus = request.query_corpus.to_dto()
                request.query_corpus.source_lang = langs_bo.get_lang(request.query_corpus.source_lang)
                request.query_corpus.target_lang = langs_bo.get_lang(request.query_corpus.target_lang)

                if request.custom_corpus:
                    request.custom_corpus = request.custom_corpus.to_dto()
                    request.custom_corpus.location = None

                pending_requests.append(request)

            ret = pending_requests
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_pending_tasks.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None

    def get_user(self, user_id: int):
        '''
        Retrieves a given user from the DB
        '''
        try:
            user_model = self.session.query(Users).get(user_id)
            if user_model == None:
                return None
            ret = user_model.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_user.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            

