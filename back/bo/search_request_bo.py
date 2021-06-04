from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from back.dto.search_request import SearchRequest

from back.models import SearchRequests, Users, BaseCorpora, Langs
from back.config import Config

from datetime import *

from back.utils import *

class SearchRequestBO:
    '''
    Business Objects for SearchRequest DTO objects
    '''
    Session = sessionmaker(Config.db)
    session = Session()

    def get_search_requests(self, limit=None, offset=0, sort_field="id", sort_dir="asc"):
        '''
        Retrieves the list of all search requests
        '''                
        try:
            order = text(SearchRequests.__tablename__+"."+sort_field+" "+sort_dir)
            lang_src = aliased(Langs)
            lang_trg = aliased(Langs)
            lang_search = aliased(Langs)

            request_models_array = self.session.query(SearchRequests, Users, BaseCorpora, lang_search, lang_src, lang_trg).filter(SearchRequests.owner == Users.id, SearchRequests.base_corpus==BaseCorpora.id, SearchRequests.search_lang==lang_search.id, BaseCorpora.source_lang==lang_src.id, BaseCorpora.target_lang==lang_trg.id).order_by(order).offset(offset).limit(limit)
            ret = build_search_requests_array(request_models_array)
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_search_requests.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            

    def get_user_search_requests(self, user_id:int, limit=None, offset=0, sort_field="id", sort_dir="asc"):
        '''
        Retrieves the list of search requests for a given user.
        '''
        try:
            order = text(SearchRequests.__tablename__+"."+sort_field+" "+sort_dir)
            lang_src = aliased(Langs)
            lang_trg = aliased(Langs)
            lang_search = aliased(Langs)
            request_models_array = self.session.query(SearchRequests, Users, BaseCorpora, lang_search, lang_src, lang_trg).filter(SearchRequests.owner == Users.id, SearchRequests.base_corpus==BaseCorpora.id, SearchRequests.search_lang==lang_search.id, SearchRequests.owner==user_id, BaseCorpora.source_lang==lang_src.id, BaseCorpora.target_lang==lang_trg.id ).order_by(order).offset(offset).limit(limit)        
            ret = build_search_requests_array(request_models_array)
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_user_search_requests.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            

    def add_search_request(self, new_request: SearchRequest):
        '''
        Adds a new SearchRequest to the system.
        '''
        try:
            new_request_model = new_request.to_model()        
            self.session.add(new_request_model)
            self.session.commit()
            ret = new_request_model.to_dto()
            self.session.close()
            return ret
        except IntegrityError  as e:
            # Error: Already existing in DB (constraint: owner, base_corpus, search_lang, search_term)
            # Then just update the date
            self.session.rollback()
            bc_id = None
            cc_id = None
            if new_request.base_corpus:
                bc_id=new_request.base_corpus.corpus_id
            if new_request.custom_corpus:
                cc_id=new_request.custom_corpus.corpus_id              

            stored_request_model = self.session.query(SearchRequests).filter(SearchRequests.owner==new_request.owner.user_id, SearchRequests.base_corpus==bc_id, SearchRequests.search_lang==new_request.search_lang.lang_id, SearchRequests.search_term==new_request.search_term).first()
            stored_request_model.creation_date = datetime.now()                
            stored_request_model.search_type = new_request.search_type
            self.session.commit()
            ret = stored_request_model.to_dto() 
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.add_search_request.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None




    def clear_user_search_history(self, user_id: int):
        '''
        Removes the searches for a given user.
        '''
        try:
            self.session.query(SearchRequests).filter(SearchRequests.owner == user_id).delete()
            self.session.commit()
            self.session.close()
            return None
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.clear_user_search_history.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            

    def remove_search_history_entry(self, search_id: int):
        '''
        Removes one search request, given its ID
        '''
        try:
            self.session.query(SearchRequests).filter(SearchRequests.id == search_id).delete()
            self.session.commit()
            self.session.close()
            return None
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.remove_search_history_entry.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            
def build_search_requests_array(resp):
    '''
    Given a array of SearchRequest model objects,
    returns a array of SearchRequest DTO objects.
    '''
    requests = []
    for model in resp:
        #SearchRequests, Users, BaseCorpora, Langs
        request = model[0].to_dto()
        user = model[1].to_dto()
        basecorpus = model[2].to_dto()
        lang_search = model[3].to_dto()
        lang_src = model[4].to_dto()
        lang_trg = model[5].to_dto()
        request.owner = user
        basecorpus.source_lang=lang_src
        basecorpus.target_lang=lang_trg
        request.base_corpus = basecorpus
        request.search_lang = lang_search
        requests.append(request)
    return requests


#TO DO:  Not finished, not fully tested
