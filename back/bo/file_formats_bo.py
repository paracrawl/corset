from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from back.models import FileFormats
from back.dto.file_format import FileFormat
from back.config import Config

from back.utils import * 

class FileFormatsBO:
    '''
    Business Objects for FileFormat DTO objects
    '''
    Session = sessionmaker(Config.db)
    session = Session()


    def get_fileformats(self, include_inactive=False,limit=None, offset=0, sort_field="id", sort_dir="asc"):
        '''
        Retrieves the list of all available active fileformats (if include_inactive, include those that are inactive as well)
        '''
        try:
            order = text( sort_field+" "+sort_dir)
            if include_inactive:
                fileformat_models_array = self.session.query(FileFormats).order_by(order).offset(offset).limit(limit)
            else:
                fileformat_models_array = self.session.query(FileFormats).filter(FileFormats.is_active==True).order_by(order).offset(offset).limit(limit)
            ret = build_fileformats_array(fileformat_models_array)
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_fileformats.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
        

    def add_fileformat(self, new_fileformat: FileFormat):
        '''
        Adds a new fileformat
        '''
        try:
            new_fileformat_model = new_fileformat.to_model()
            self.session.add(new_fileformat_model)
            self.session.commit()
            ret = new_fileformat_model.to_dto()
            self.session.close()
            return ret
        except IntegrityError as ex:
            #Error: Already existing in DB            
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.add_fileformat.__name__, ex)
            logging.exception(msg)
            raise AlreadyExisting(msg) from None
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.add_fileformat.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None


    def get_fileformat(self, fileformat_id: int):
        '''
        Retrieves a fileformat, given its fileformat_id
        '''
        try:
            fileformat_model = self.session.query(FileFormats).get(fileformat_id)
            if fileformat_model == None:
                return None
            ret = fileformat_model.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_fileformat.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None


    def modify_fileformat(self, modified_fileformat: FileFormat):
        '''
        Modifies a fileformat
        '''
        try:
            modified_fileformat_model = modified_fileformat.to_model()
            old_fileformat_model = self.session.query(FileFormats).get(modified_fileformat_model.id)
            old_fileformat_model.update(modified_fileformat_model) #The update function asserts the id is the same
            self.session.commit()
            ret = old_fileformat_model.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.modify_fileformat.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None            


    def toggle_fileformat_active(self, fileformat_id: int, active: bool):
        '''
        Marks a given fileformat as active/not active.
        '''
        try:
            fileformat = self.session.query(FileFormats).get(fileformat_id)
            fileformat.is_active = active
            self.session.commit()
            ret = fileformat.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.toggle_fileformat_active.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            


def build_fileformats_array(resp):
    '''
    Given a array of FileFormats model objects,
    returns a array of FileFormat DTO objects.
    '''
    fileformats = []
    for fileformat_model in resp:
        fileformat = fileformat_model.to_dto()
        fileformats.append(fileformat)
    return fileformats
