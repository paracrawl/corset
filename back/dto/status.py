from dataclasses import dataclass

from dataclasses_json import dataclass_json

import back.models as models


@dataclass_json
@dataclass
class Status:
    '''
    Status of a given job (Query Request) in the system.
    '''
    status_id: int
    status: str
    is_active: bool

    def to_model(self):
        '''
        Returns a Status model object
        based on the invoking Status DTO objec.
        '''
        status_model=models.Statuses(id=self.status_id, status=self.status, is_active=self.is_active)
        return status_model
