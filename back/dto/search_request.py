from dataclasses import dataclass, field
from datetime import datetime

from dataclasses_json import dataclass_json

import back.models as models

from .base_corpus import BaseCorpus
from .custom_corpus import CustomCorpus
from .lang import Lang
from .user import User


@dataclass_json
@dataclass
class SearchRequest:
    '''
    A simple search request made by a user. We keep track (of requests, not responses)  so we can show users their Search History.
    “rows” and “start” is the info needed for pagination (sentences per page and offset), not stored in DB.
    '''


    search_id: int
    owner: User
    creation_date: datetime
    base_corpus: BaseCorpus
    custom_corpus: CustomCorpus
    search_lang: Lang
    search_field: str
    search_term: str
    search_type: str
    rows: int
    start: int


    def __init__(self, search_id, owner, creation_date, base_corpus, custom_corpus, search_lang, search_field, search_term, search_type, rows, start):
        self.search_id = search_id
        self.owner = owner
        self.creation_date = creation_date
        self.base_corpus = base_corpus
        self.custom_corpus = custom_corpus
        self.search_lang = search_lang
        self.search_field = search_field
        self.search_term = search_term
        self.search_type = search_type
        self.rows = rows
        self.start = start
        
        assert ((self.base_corpus != None and self.custom_corpus==None) or (self.base_corpus==None and self.custom_corpus!= None))
        assert (self.search_field in ["src", "trg"])

        if self.search_lang==None or self.search_lang=="":
            if self.search_field == "src":
                if self.base_corpus != None:
                    self.search_lang = self.base_corpus.source_lang
                else:
                    self.search_lang = self.custom_corpus.source_lang
            else:
                if self.base_corpus != None:
                    self.search_lang = self.base_corpus.target_lang
                else:
                    self.search_lang = self.custom_corpus.target_lang        
        
    
    def to_model(self):
        '''
        Returns a SearchRequest model object based on the invoknig SearchRequest DTO object.
        '''
        bc_id = None
        cc_id = None
        if self.base_corpus:
            bc_id = self.base_corpus.corpus_id
        if self.custom_corpus:
            cc_id = self.custom_corpus.corpus_id    
        

                    
        searchrequest_model = models.SearchRequests(id=self.search_id, owner=self.owner.user_id, creation_date=self.creation_date, base_corpus=bc_id, custom_corpus=cc_id, search_lang=self.search_lang.lang_id, search_field=self.search_field, search_term=self.search_term, search_type=self.search_type)
        return searchrequest_model
