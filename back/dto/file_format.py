from dataclasses import dataclass

from dataclasses_json import dataclass_json

import back.models as models


@dataclass_json
@dataclass
class FileFormat:
    '''
    Possible formats for query corpora and custom corpora.
    Possible values: tmx, txt.
    '''
    format_id: int
    file_format: str
    is_active: bool

    def to_model(self):
        '''
        Returns a FileFormat model object based on the invoknig FileFormat DTO object.
        '''
        fileformat_model = models.FileFormats(id=self.format_id, file_format=self.file_format, is_active=self.is_active)
        return fileformat_model
