from dataclasses import dataclass
from typing import List

from datetime import datetime

from dataclasses_json import dataclass_json

import back.models as models

from .corpus import Corpus
from .file_format import FileFormat
#from .query_request import QueryRequest
from .tag import Tag


@dataclass_json
@dataclass
class CustomCorpus(Corpus):
    '''
    Inherits from Corpus.
    A Custom Corpus is the response subset produced after a Base Corpus is queried with a Query Corpus.
    Custom Corpora is stored .tar.gz in the disk, and a preview stored in solr.
    '''
    
    #corpus_id: int
    location: str
    description: str
    file_format: FileFormat
    solr_prefix: str
    topics: List[Tag]
    last_download: datetime
    num_downloads: int
    is_private: bool
    creation_date: datetime

    def to_model(self):
        '''
        Returns a CustomCorpora model object based on the invoking BaseCorpus DTO object.
        '''
        corpus_model = models.CustomCorpora(id=self.corpus_id, name=self.name,
                                            source_lang=self.source_lang, target_lang=self.target_lang,
                                            sentences=self.sentences, size_mb=self.size,
                                            solr_collection=self.solr_collection,
                                            is_active=self.is_active, is_highlight=self.is_highlight,
                                            description=self.description,
                                            file_format=self.file_format, location=self.location,
                                            solr_prefix=self.solr_prefix, topics=self.topics,
                                            last_download=self.last_download, num_downloads=self.num_downloads,
                                            is_private=self.is_private, creation_date=self.creation_date)
                
        return corpus_model
