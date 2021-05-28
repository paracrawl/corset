from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

import back.models as models

from .file_format import FileFormat
from .lang_format import LangFormat
from .lang import Lang


@dataclass_json
@dataclass
class QueryCorpus():
    '''
    These are corpora uploaded by users, in order to be used as “search” for similar text in Base Corpora.
    After finishing their processing, they must be removed from the disk.
    '''
    file_format: FileFormat
    lang_format: LangFormat
    source_lang: Lang
    target_lang: Lang
    sentences: int
    size: int
    location: str
    is_active: bool
    corpus_id: int = -1

    def to_model(self):
        '''
        Returns a QueryCorpora model object baesd on the invoking QueryCorpora DTO object.
        '''
        corpus_model = models.QueryCorpora(source_lang=self.source_lang.lang_id, target_lang=self.target_lang.lang_id,
                                           file_format=self.file_format.format_id,
                                           lang_format=self.lang_format.format_id,
                                           sentences=self.sentences, size_mb=self.size, location=self.location,
                                           is_active=self.is_active)
        return corpus_model
