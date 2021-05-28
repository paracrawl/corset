from dataclasses import dataclass

from dataclasses_json import dataclass_json

import back.models as models


@dataclass_json
@dataclass
class Tag:
    '''
    Tags for sentences, in order to identify domains, for example.
    These are stored in Solr.
    '''
    tag_id: int
    tag: str
    is_active: bool
    
    def to_model(self):
        '''
        Returns a Tags model object
        based on the invoking Tag DTO object
        '''
        tag_model=models.Tags(id=self.tag_id, tag=self.tag, is_active=self.is_active)
        return tag_model
