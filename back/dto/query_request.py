from dataclasses import dataclass
from datetime import datetime

from dataclasses_json import dataclass_json

from .base_corpus import BaseCorpus
from .custom_corpus import CustomCorpus
from .query_corpus import QueryCorpus
from .status import Status
from .user import User

import back.models as models


@dataclass_json
@dataclass
class QueryRequest:
    '''
    When a user queries a Base Corpus with a Query Corpus, it produces a Query Request.
    A Query Request produces a Custom Corpus, after finishing.
    A Query Request has an owner (the user performing the request) and a name, which will be used as well as the Custom Corpus name.
    Since Query Requests play a “queue job” role, the job status and the identifier used in the external queue (celery?) for the job will be included in this object.
    '''
    owner: User
    name: str
    creation_date: datetime
    base_corpus: BaseCorpus
    query_corpus: QueryCorpus
    job_id: str
    status: Status
    request_id: int = -1
    custom_corpus: CustomCorpus = None

    def to_model(self):
        '''
        Returns a QueryRequest model object based on the invoknig QueryRequest DTO object.
        '''
        
        #Custom corpus might be None if not yet created
        cc_id=None        
        if self.custom_corpus:
            cc_id = self.custom_corpus
        
        queryrequest_model = models.QueryRequests(owner=self.owner, name=self.name,
                                                  creation_date=self.creation_date,
                                                  base_corpus=self.base_corpus,
                                                  query_corpus=self.query_corpus,
                                                  job=self.job_id, status=self.status)

        return queryrequest_model
