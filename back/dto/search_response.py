from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json

from .search_request import SearchRequest
from .sentence import Sentence


@dataclass_json
@dataclass
class SearchResponse:
    '''
    The response produced by a Search Request.
    These are not stored in DB.
    “sentences” is the total amount of occurrences of the search term.
    “rows” and “start” is the info needed for pagination (sentences per page and offset)
    '''
    request: SearchRequest
    occurrences: int
    rows: int
    start: int
    results: List[Sentence]
