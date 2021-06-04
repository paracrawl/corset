from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from back.models import Tags
from back.dto.tag import Tag
from back.config import Config

from back.utils import *

class TagsBO:
    '''
    Business Objects for Tag DTO objects
    '''
    Session = sessionmaker(Config.db)
    session = Session()


    def get_tags(self, include_inactive=False, limit=None, offset=0, sort_field="id", sort_dir="asc"):
        '''
        Retrieves the list of all available active tags (if include_inactive, include those that are inactive as well)
        '''
        try:
            order = text(sort_field+" "+sort_dir)
            if include_inactive:
                tag_models_array = self.session.query(Tags).order_by(order).offset(offset).limit(limit)
            else:
                tag_models_array = self.session.query(Tags).filter(Tags.is_active==True).order_by(order).offset(offset).limit(limit)
            ret = build_tags_array(tag_models_array)
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close() 
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_tags.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            


    def add_tag(self,new_tag:Tag):
        '''
        Adds a new tag
        '''
        try:
            new_tag_model = new_tag.to_model()
            self.session.add(new_tag_model)
            self.session.commit()
            ret = new_tag_model.to_dto()
            self.session.close()
            return ret
        except IntegrityError as ex:
            #Error: Already existing in DB            
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.add_tag.__name__, ex)
            logging.exception(msg)
            raise AlreadyExisting(msg) from None
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.add_tag.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None


    def get_tag(self, tag_id: int):
        '''
        Retrieves a tag, given its tag_id
        '''
        try:
            tag_model = self.session.query(Tags).get(tag_id)
            if tag_model == None:
                return None
            ret = tag_model.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_tag.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            
            

    def modify_tag(self, modified_tag: Tag):
        '''
        Modifies a tag
        '''
        try:
            modified_tag_model = modified_tag.to_model()
            old_tag_model = self.session.query(Tags).get(modified_tag_model.id)
            old_tag_model.update(modified_tag_model) #The update function asserts the id is the same
            self.session.commit()
            ret = old_tag_model.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.modify_tag.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            


    def toggle_tag_active(self, tag_id: int, active: bool):
        '''
        Marks a given tag as active/not active.
        '''
        try:
            tag = self.session.query(Tags).get(tag_id)
            tag.is_active = active
            self.session.commit()
            ret = tag.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.toggle_tag_active.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            


def build_tags_array(resp):
    '''
    Given a array of Tag model objects,
    returns a array of Tag DTO objects.
    '''
    tags = []
    for tag_model in resp:
        tag = tag_model.to_dto()
        tags.append(tag)
    return tags
