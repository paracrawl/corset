from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from back.models import Langs
from back.dto.lang import Lang
from back.config import Config

from back.utils import *

class LangsBO:
    '''
    Business Objects for Lang DTO objects
    '''
    Session = sessionmaker(Config.db)
    session = Session()


    def get_langs(self, include_inactive=False, limit=None, offset=0, sort_field="name", sort_dir="asc"):
        '''
        Retrieves the list of all available active languages (if include_inactive, include those that are inactive as well)
        '''
        try:
            order = text(sort_field+" "+sort_dir)
            if include_inactive:
                lang_models_array = self.session.query(Langs).order_by(order).offset(offset).limit(limit)
            else:
                lang_models_array = self.session.query(Langs).filter(Langs.is_active==True).order_by(order).offset(offset).limit(limit)
            ret = build_langs_array(lang_models_array)
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_langs.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            


    def add_lang(self,new_lang: Lang):
        '''
        Adds a new language
        '''
        try:
            new_lang_model = new_lang.to_model()
            self.session.add(new_lang_model)
            self.session.commit()
            ret = new_lang_model.to_dto()
            self.session.close()
            return ret
        except IntegrityError as ex:
            #Error: Already existing in DB            
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.add_lang.__name__, ex)
            logging.exception(msg)
            raise AlreadyExisting(msg) from None
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.add_lang.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None



    def get_lang(self, lang_id: int):
        '''
        Retrieves a language, given its lang_id
        '''
        try:
            lang_model = self.session.query(Langs).get(lang_id)
            if lang_model == None:
                return None
            ret = lang_model.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_lang.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            

    def get_lang_by_code(self, lang_code: str):
        '''
        Retrieves a language, given its code
        '''
        try:
            lang_model = self.session.query(Langs).filter_by(lang_code=lang_code).one()
            if lang_model == None:
                return None
            ret = lang_model.to_dto()
            self.session.close()
            return ret
        except Exception as ex:        
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_lang_by_code.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
    

    def modify_lang(self, modified_lang: Lang):
        '''
        Modifies a language
        '''
        try:
            modified_lang_model = modified_lang.to_model()
            old_lang_model = self.session.query(Langs).get(modified_lang_model.id)
            old_lang_model.update(modified_lang_model) # The update function asserts the id is the same
            self.session.commit()
            ret = old_lang_model.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.sesion.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.modify_lang.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            


    def toggle_lang_active(self,lang_id: int, active: bool):
        '''
        Marks a given language as active/not active.
        '''
        try:
            lang = self.session.query(Langs).get(lang_id)
            lang.is_active = active
            self.session.commit()
            ret = lang.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.toggle_lang_active.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            


def build_langs_array(resp):
    '''
    Given a array of Lang model objects,
    returns a array of Lang DTO objects.
    '''
    langs = []
    for lang_model in resp:
        lang = lang_model.to_dto()
        langs.append(lang)
    return langs
