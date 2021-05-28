from dataclasses import dataclass

from .lang import Lang


@dataclass
class Corpus:
    '''
    Abstract/interface class, for BaseCorpus and QueryCorpus to inherit.
    '''
    corpus_id: int
    name: str
    source_lang: Lang
    target_lang: Lang
    sentences: int
    size: int
    solr_collection: str
    is_active: bool
    is_highlight: bool
