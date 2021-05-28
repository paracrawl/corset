from dataclasses import dataclass

from dataclasses_json import dataclass_json

import back.models as models


@dataclass_json
@dataclass
class Lang:
    '''
    Languages accepted by the application.
    '''
    lang_id: int
    code: str
    name: str
    is_active: bool

    def to_model(self):
        '''
        Returns a Lang model object baed on the invoking Lang DTO object.
        '''
        lang_model = models.Langs(id=self.lang_id, lang_code=self.code, name=self.name, is_active=self.is_active)
        return lang_model
