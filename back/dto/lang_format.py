from dataclasses import dataclass

from dataclasses_json import dataclass_json

import back.models as models


@dataclass_json
@dataclass
class LangFormat:
    '''
     Possible formats for query corpora (custom corpora is always bilingual/parallel).
     Possible values: mono, parallel.
    '''
    format_id: int
    lang_format: str
    is_active: bool

    def to_model(self):
        '''
        Returns a  LangFormat model object based on the invoking LangFormat DTO object.
        '''
        langformat_model = models.LangFormats(id=self.format_id, lang_format=self.lang_format, is_active=self.is_active)
        return langformat_model
