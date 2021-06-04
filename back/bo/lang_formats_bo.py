from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from back.models import LangFormats
from back.dto.lang_format import LangFormat
from back.config import Config

from back.utils import *

class LangFormatsBO:
    '''
    Business Objects for LangFormat DTO objects
    '''
    Session = sessionmaker(Config.db)
    session = Session()


    def get_langformats(self, include_inactive=False,limit=None, offset=0, sort_field="id", sort_dir="asc"):
        '''
        Retrieves the list of all available active langformats (if include_inactive, include those that are inactive as well)
        '''
        try:
            order = text(sort_field+" "+sort_dir)
            if include_inactive:
                langformat_models_array = self.session.query(LangFormats).order_by(order).offset(offset).limit(limit)
            else:
                langformat_models_array = self.session.query(LangFormats).filter(LangFormats.is_active==True).order_by(order).offset(offset).limit(limit)
            ret = build_langformats_array(langformat_models_array)
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_langformats.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None



    def add_langformat(self, new_langformat: LangFormat):
        '''
        Adds a new langformat
        '''
        try:	
            new_langformat_model = new_langformat.to_model()
            self.session.add(new_langformat_model)
            self.session.commit()
            ret = new_langformat_model.to_dto()
            self.session.close()
            return ret
        except IntegrityError as ex:
            #Error: Already existing in DB            
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.add_langformat.__name__, ex)
            logging.exception(msg)
            raise AlreadyExisting(msg) from None
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.add_langformat.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None


    def get_langformat(self, langformat_id: int):
        '''
        Retrieves a langformat, given its langformat_id
        '''
        try:
            langformat_model = self.session.query(LangFormats).get(langformat_id)
            if langformat_model == None:
                return None
            ret = langformat_model.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_langformat.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            

    def modify_langformat(self, modified_langformat: LangFormat):
        '''
        Modifies a langformat
        '''
        try:
            modified_langformat_model = modified_langformat.to_model()
            old_langformat_model = self.session.query(LangFormats).get(modified_langformat_model.id)
            old_langformat_model.update(modified_langformat_model) #The update function asserts the id is the same
            self.session.commit()
            ret = old_langformat_model.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.modify_langformat.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None


    def toggle_langformat_active(self, langformat_id: int, active: bool):
        '''
        Marks a given langformat as active/not active.
        '''
        try:
            langformat = self.session.query(LangFormats).get(langformat_id)
            langformat.is_active = active
            self.session.commit()
            ret = langformat.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.toggle_langformat_active.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            


def build_langformats_array(resp):
    '''
    Given a array of LangFormats model objects,
    returns a array of LangFormat DTO objects.
    '''
    langformats = []
    for langformat_model in resp:
        langformat = langformat_model.to_dto()
        langformats.append(langformat)
    return langformats
