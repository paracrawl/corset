from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from back.models import Statuses
from back.dto.status import Status
from back.config import Config

from back.utils import *

class StatusBO:
    '''
    Business Objects for Status DTO objects
    '''
    Session = sessionmaker(Config.db)
    session = Session()


    def get_statuses(self, include_inactive=False, limit=None, offset=0, sort_field="id", sort_dir="asc"):
        '''
        Retrieves the list of all available active statuses (if include_inactive, include those that are inactive as well)
        '''
        try:
            order = text(sort_field+" "+sort_dir)
            if include_inactive:
                status_models_array = self.session.query(Statuses).order_by(order).offset(offset).limit(limit)
            else:
                status_models_array = self.session.query(Statuses).filter(Statuses.is_active==True).order_by(order).offset(offset).limit(limit)
            ret = build_statuses_array(status_models_array)
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_statuses.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            

    def add_status(self,new_status: Status):
        '''
        Adds a new status
        '''
        try:
            new_status_model = new_status.to_model()
            self.session.add(new_status_model)
            self.session.commit()
            ret = new_status_model.to_dto()
            self.session.close()
            return ret
        except IntegrityError as ex:
            #Error: Already existing in DB            
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.add_status.__name__, ex)
            logging.exception(msg)
            raise AlreadyExisting(msg) from None
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.add_status.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None



    def get_status(self, status_id: int):
        '''
        Retrieves a status, given its status_id
        '''
        try:
            status_model = self.session.query(Statuses).get(status_id)
            if status_model == None:
                return None
            ret = status_model.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_status.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            

    def modify_status(self, modified_status: Status):
        '''
        Modifies a status
        '''
        try:
            modified_status_model = modified_status.to_model()
            old_status_model = self.session.query(Statuses).get(modified_status_model.id)
            old_status_model.update(modified_status_model) #The update function asserts the id is the same
            self.session.commit()
            ret = old_status_model.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.modify_status.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            


    def toggle_status_active(self,status_id: int, active: bool):
        '''
        Marks a given status as active/not active.
        '''
        try:
            status = self.session.query(Statuses).get(status_id)
            status.is_active = active
            self.session.commit()
            ret = status.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.toggle_status_active.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None


def build_statuses_array(resp):
    '''
    Given a array of Status model objects,
    returns a array of Status DTO objects.
    '''
    statuses = []
    for status_model in resp:
        status = status_model.to_dto()
        statuses.append(status)
    return statuses
