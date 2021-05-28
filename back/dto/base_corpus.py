from dataclasses import dataclass

from dataclasses_json import dataclass_json

import back.models as models

from .corpus import Corpus


@dataclass_json
@dataclass
class BaseCorpus(Corpus):
    '''
    Inherits from Corpus. These are the “original” corpora (for example:  Paracrawl EN-ES, Paracrawl EN-DE, etc).
    These are stored in Solr, and they are not changeable.
    They must be uploaded to Solr outside the DataPortal application (at least, in this first version).
    '''
    description: str

    def to_model(self):
        '''
        Returns a BaseCorpora model object based on the invoking BaseCorpus DTO object.
        '''
        corpus_model = models.BaseCorpora(id=self.corpus_id, name=self.name, source_lang=self.source_lang, target_lang=self.target_lang, sentences=self.sentences, size_mb=self.size, solr_collection=self.solr_collection, is_active=self.is_active, is_highlight=self.is_highlight, description=self.description)
        return corpus_model
