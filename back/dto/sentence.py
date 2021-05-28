from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json

from .tag import Tag


@dataclass_json
@dataclass
class Sentence:
    '''
    Each one of the sentences returned by Solr after a Search Request.
    These are not stored in DB (the ID is the sentence index from Solr).
    More fields will be added when Solr structure for collections  is defined.
    '''
    solr_id: str
    source: str
    target: str
    score: float
    tags: List[Tag]
