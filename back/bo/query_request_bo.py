from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from back.bo.custom_corpus_bo import CustomCorpusBO
from back.bo.langs_bo import LangsBO
from back.dto.query_request import QueryRequest

from back.models import QueryRequests, Users, BaseCorpora, QueryCorpora, CustomCorpora, Statuses
from back.config import Config

from back.utils import *


class QueryRequestBO:
    '''
    Business Objects for QueryRequest DTO objects
    '''
    Session = sessionmaker(Config.db)
    session = Session()


    def get_query_requests(self, limit=None, offset=0, sort_field="id", sort_dir="asc"):
        '''
        Retrieves the list of all query requests.
        '''
        try:
            order = text(QueryRequests.__tablename__ +"."+sort_field+" "+sort_dir)

            requests_model_array = self.session.query(QueryRequests, Users, BaseCorpora, QueryCorpora, Statuses).filter(QueryRequests.owner==Users.id, QueryRequests.base_corpus==BaseCorpora.id,
                                    QueryRequests.query_corpus==QueryCorpora.id, QueryRequests.status==Statuses.id).order_by(order).offset(offset).limit(limit) 
            ret = build_query_requests_array(requests_model_array)
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_query_requests.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            

    def add_query_request(self, new_request: QueryRequest):
        '''
        Adds a new QueryRequest to the system.
        '''
        try:
            new_request_model = new_request.to_model()
            self.session.add(new_request_model)
            self.session.commit()
            ret = new_request_model.to_dto()
            self.session.close()
            return ret
        except IntegrityError as ex:
            #Error: Already existing in DB            
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.add_query_request.__name__, ex)
            logging.exception(msg)
            raise AlreadyExisting(msg) from None
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.add_query_request.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            
            

    def get_user_query_requests(self,  user_id:int, limit=None, offset=0, sort_field="id", sort_dir="asc"):
        '''
        Retrieves the list of query requests for a given user.
        '''
        try:
            order = text(QueryRequests.__tablename__+"."+sort_field+" "+sort_dir)
            request_models_array = self.session.query(QueryRequests, Users, BaseCorpora, QueryCorpora, Statuses).filter(QueryRequests.owner==user_id, QueryRequests.owner==Users.id, QueryRequests.base_corpus==BaseCorpora.id,
                                            QueryRequests.query_corpus==QueryCorpora.id,  QueryRequests.status==Statuses.id).order_by(order).offset(offset).limit(limit) 
            ret = build_query_requests_array(request_models_array)
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_user_query_requests.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            

    def get_query_request(self, request_id:int):
        '''
        Retrieves the metadata for a given QueryRequest.
        '''
        try:
            model=self.session.query(QueryRequests, Users, BaseCorpora, QueryCorpora, Statuses).filter(QueryRequests.id==request_id, QueryRequests.owner == Users.id, QueryRequests.base_corpus==BaseCorpora.id,QueryRequests.query_corpus==QueryCorpora.id,  QueryRequests.status==Statuses.id).first()
            if model == None:
                return None            
            query_request=model[0].to_dto()
            user=model[1].to_dto()
            base_corpus=model[2].to_dto()
            query_corpus=model[3].to_dto()
            status=model[4].to_dto()
            custom_corpus=None
            if query_request.custom_corpus != None:
                cc_bo = CustomCorpusBO()
                custom_corpus = cc_bo.get_custom_corpus(query_request.custom_corpus)
            query_request.owner=user
            query_request.base_corpus=base_corpus
            query_request.query_corpus=query_corpus
            query_request.custom_corpus=custom_corpus
            query_request.status=status
            self.session.close()
            return query_request
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_query_request.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None


    def update_query_request_status(self, request_id:int, status_id:int):
        '''
        Changes the status of a given QueryRequest
        '''
        try:
            request = self.session.query(QueryRequests).get(request_id)
            request.status=status_id
            self.session.commit()
            ret = request.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.update_query_request_status.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None

    def update_query_request_custom_corpus(self, request_id:int, corpus_id: int):
        '''
        Updates the custom corpus of a given QueryRequest
        '''
        try:
            request = self.session.query(QueryRequests).get(request_id)
            request.custom_corpus=corpus_id
            self.session.commit()
            ret = request.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.update_query_request_custom_corpus.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None


    def get_public_custom_corpora_requests(self,  limit=None, offset=0, sort_field="id", sort_dir="asc"):
        '''
        Retrieves all query requests having public custom corpora
        '''
        try:
            order = text(QueryRequests.__tablename__+"."+sort_field+" "+sort_dir)
            request_models_array = self.session.query(QueryRequests, Users, BaseCorpora, QueryCorpora, Statuses, CustomCorpora)\
                                    .filter(QueryRequests.status==5, QueryRequests.owner==Users.id, QueryRequests.base_corpus==BaseCorpora.id,
                                            QueryRequests.query_corpus==QueryCorpora.id, QueryRequests.status==Statuses.id,
                                            QueryRequests.custom_corpus!=None,
                                            QueryRequests.custom_corpus==CustomCorpora.id, CustomCorpora.is_private==False,
                                            CustomCorpora.is_active==True).order_by(order).offset(offset).limit(limit)
            ret = build_query_requests_array(request_models_array)
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_public_custom_corpora_requests.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            

    def get_popular_custom_corpora_requests(self, limit=10):
        '''
        Retrieves the most downloaded  public and active corsets.
        '''
        try:
            order = text("customcorpora.num_downloads desc")
            request_models_array = self.session.query(QueryRequests, Users, BaseCorpora, QueryCorpora, Statuses, CustomCorpora).filter(QueryRequests.status==5, QueryRequests.owner==Users.id, QueryRequests.base_corpus==BaseCorpora.id,
                                            QueryRequests.query_corpus==QueryCorpora.id,  QueryRequests.status==Statuses.id, QueryRequests.custom_corpus!=None, QueryRequests.custom_corpus==CustomCorpora.id, CustomCorpora.is_private==False, CustomCorpora.is_active==True)\
                                            .order_by(order).limit(limit)
            ret = build_query_requests_array(request_models_array)
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_popular_custom_corpora_requests.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None

        
                    
def build_query_requests_array(resp):
    '''
    Given a array of QueryRequests model objects,
    returns a array of QueryRequest DTO objects.
    '''
    requests=[]
    for model in resp:
        request = model[0].to_dto()
        user=model[1].to_dto()
        base_corpus=model[2].to_dto()
        query_corpus=model[3].to_dto()
        status=model[4].to_dto()
        custom_corpus=None
        if request.custom_corpus != None:
            cc_bo = CustomCorpusBO()
            custom_corpus = cc_bo.get_custom_corpus(request.custom_corpus)

        request.owner = user
        request.base_corpus=base_corpus
        request.query_corpus=query_corpus
        if request.query_corpus:
            langs_bo = LangsBO()
            request.query_corpus.source_lang = langs_bo.get_lang(request.query_corpus.source_lang)
            request.query_corpus.target_lang = langs_bo.get_lang(request.query_corpus.target_lang)

        request.custom_corpus=custom_corpus
        request.status=status
        requests.append(request)
    return requests
