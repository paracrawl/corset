from datetime import datetime

from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.types import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

from back.dto.base_corpus import BaseCorpus
from back.dto.lang import Lang
from back.dto.file_format import FileFormat
from back.dto.lang_format import LangFormat
from back.dto.status import Status
from back.dto.tag import Tag

from back.dto.user import User
from back.dto.custom_corpus import CustomCorpus
from back.dto.query_corpus import QueryCorpus
from back.dto.search_request import SearchRequest
from back.dto.query_request import QueryRequest

base = declarative_base()

class BaseCorpora(base):
    '''
    SQLAlchemy model for basecorpora table and BaseCorpus DTO objects.
    '''
    __tablename__ = "basecorpora"
    id  = Column(Integer, primary_key=True)
    name = Column(String(200))
    description = Column(String(1000))
    source_lang = Column(Integer, ForeignKey("langs.id"), nullable=False)
    target_lang = Column(Integer, ForeignKey("langs.id"), nullable=False)
    sentences = Column(Integer, nullable=False, default=0)
    size_mb = Column(Integer, nullable=False, default=0)
    solr_collection = Column(String(500), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_highlight = Column(Boolean, nullable=False, default=True)
    
    def to_dto(self):
        '''
        Given a BaseCorpora model object,
        builds and returns a BaseCorpus DTO object based on it.
        '''
        corpus_dto = BaseCorpus(corpus_id=self.id, name=self.name, source_lang=self.source_lang, target_lang=self.target_lang, sentences=self.sentences, size=self.size_mb, solr_collection=self.solr_collection, is_active=self.is_active, is_highlight=self.is_highlight, description=self.description)
        return corpus_dto

    def update(self, corpus: 'BaseCorpora'):
        '''
        Overwrites the attributes on the invoking BaseCorpora object
        based another one passed as parameter.
        '''
        assert self.id == corpus.id #ToDo: Manage this!
        self.name = corpus.name
        self.description = corpus.description
        self.source_lang = corpus.source_lang
        self.target_lang = corpus.target_lang
        self.sentences = corpus.sentences
        self.size_mb = corpus.size_mb
        self.solr_collection = corpus.solr_collection
        self.is_active = corpus.is_active
        self.is_highlight = corpus.is_highlight

class QueryCorpora(base):
    '''
    SQLAlchemy model for querycorpora table and QueryCopus DTO objects.
    '''
    __tablename__ = "querycorpora"
    id = Column(Integer, primary_key=True)
    file_format = Column(Integer, ForeignKey("fileformats.id"), nullable=False)
    lang_format = Column(Integer, ForeignKey("langformats.id"), nullable=False)
    source_lang = Column(Integer, ForeignKey("langs.id"), nullable=False)
    target_lang = Column(Integer, ForeignKey("langs.id"), nullable=True)
    sentences = Column(Integer, nullable=False, default=0)
    size_mb = Column(Integer, nullable=False, default=0)
    location = Column(String(1000), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    def to_dto(self):
        '''
        Given a QueryCorpora model object,
        builds and returns a QueryCorpus DTO object based on it.
        '''
        corpus_dto = QueryCorpus(corpus_id=self.id, file_format=self.file_format, lang_format=self.lang_format, source_lang=self.source_lang, target_lang=self.target_lang, sentences=self.sentences, size=self.size_mb, location=self.location, is_active=self.is_active)
        return corpus_dto


    def update(self, corpus: 'QueryCorpora'):
        '''
        Overwrites the attributes on the invoking QueryCorpora object,
        based on another one passed as parameter.
        '''
        assert self.id == corpus.id #ToDo: Manage this!
        self.file_format=corpus.file_format
        self.lang_format=corpus.file_format
        self.source_lang=corpus.source_lang
        self.target_lang=corpus.target_lang
        self.sentences=corpus.sentences
        self.size_mb=corpus.size
        self.location=corpus.location
        self.is_active=corpus.is_active


class CustomCorpora(base):
    '''
    SQLAlchemy model for customcorpora table and CustomCorpus DTO objects.
    '''
    __tablename__ = "customcorpora"
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    description = Column(String(1000))
    file_format = Column(Integer, ForeignKey("fileformats.id"), nullable=False)
    source_lang = Column(Integer, ForeignKey("langs.id"), nullable=False)
    target_lang = Column(Integer, ForeignKey("langs.id"), nullable=False)
    sentences = Column(Integer, nullable=False, default=0)
    size_mb = Column(Integer, nullable=False, default=0)
    location = Column(String(1000), nullable=False)
    solr_collection = Column(String(500), nullable=False)
    solr_prefix = Column(String(200), nullable=False)
    topics = Column(ARRAY(Integer))
    last_download = Column(DateTime, nullable=False)
    num_downloads = Column(Integer, nullable=False, default=0)
    is_private = Column(Boolean, nullable=False, default=True)
    is_active = Column(Boolean, nullable=False, default=True)
    creation_date = Column(DateTime, nullable=False, default=datetime.now())
    is_highlight = Column(Boolean, nullable=False, default=True)


    def to_dto(self):
        custom_corpus_dto = CustomCorpus(corpus_id=self.id, name=self.name, description=self.description, file_format=self.file_format, source_lang=self.source_lang, target_lang=self.target_lang,
                             sentences=self.sentences, size=self.size_mb, location=self.location, solr_collection=self.solr_collection, solr_prefix=self.solr_prefix, topics=self.topics, last_download=self.last_download,
                             num_downloads=self.num_downloads, is_private=self.is_private, is_active=self.is_active, creation_date=self.creation_date, is_highlight=self.is_highlight)
        return custom_corpus_dto
     

class SearchRequests(base):
    '''
    SQLAlchemy model for searchrequests table and SearchRequest DTO objects.
    '''
    __tablename__ = "searchrequests"
    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey("users.id"), nullable=False)
    creation_date = Column(DateTime, nullable=False, default=datetime.now())
    base_corpus = Column(Integer, ForeignKey("basecorpora.id"), nullable=True)
    custom_corpus = Column(Integer, ForeignKey("customcorpora.id"), nullable=True)
    search_lang = Column(Integer, ForeignKey("langs.id"), nullable=False)
    search_field = Column(String(50), nullable=False)
    search_term = Column(String(200), nullable=False)
    search_type = Column(String(50), nullable=False)

    def to_dto(self):
        '''
        Given a SearchRequest model object,
        builds and returns a SearchRequest DTO object based on it.
        '''

        search_request_dto = SearchRequest(search_id=self.id, owner=self.owner, creation_date=self.creation_date, base_corpus=self.base_corpus, custom_corpus=self.custom_corpus, search_lang=self.search_lang, search_field=self.search_field, search_term=self.search_term, rows=0, start=0, search_type=self.search_type)

        #self.owner?
        #self.base_corpus?
        #self.search_lang?
        return search_request_dto

class QueryRequests(base):
    '''    
    SQLAlchemy model for queryrequests table and QueryRequest DTO objects.
    '''
    __tablename__ = "queryrequests"
    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    creation_date = Column(DateTime, nullable=False, default=datetime.now())
    base_corpus = Column(Integer, ForeignKey("basecorpora.id"), nullable=False)
    query_corpus = Column(Integer, ForeignKey("querycorpora.id"), nullable=False)
    custom_corpus = Column(Integer, ForeignKey("customcorpora.id"), nullable=False)
    job = Column(String, unique=True, nullable=False)
    status = Column(Integer, ForeignKey("status.id"), nullable=False)
    '''
    status_rel = relationship("Statuses", backref=backref("query_requests"),
                              primaryjoin="Statuses.id==QueryRequests.status")
    owner_rel = relationship("Users", primaryjoin="Users.id==QueryRequests.owner")
    base_corpus_rel = relationship("BaseCorpora", primaryjoin="BaseCorpora.id==QueryRequests.base_corpus")
    query_corpus_rel = relationship("QueryCorpora", primaryjoin="QueryCorpora.id==QueryRequests.query_corpus")
    custom_corpus_rel = relationship("CustomCorpora", primaryjoin="CustomCorpora.id==QueryRequests.custom_corpus")
    '''
    def to_dto(self):
        '''
        Given a QueryRequest model object,
        builds and return a QueryRequest DTO object based on it.
        '''
        query_request_dto = QueryRequest(request_id=self.id,
                                         owner=self.owner, name=self.name, creation_date=self.creation_date,
                                         base_corpus=self.base_corpus,
                                         query_corpus=self.query_corpus,
                                         custom_corpus=self.custom_corpus, job_id=self.job,
                                         status=self.status)
        return query_request_dto
        
        
class Users(base):
    '''
    SQLAlchemy model for users table and User DTO objects.
    '''
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    social_id = Column(String(200), nullable=False, unique=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    avatar = Column(String(200))
    creation_date = Column(DateTime, nullable=False, default=datetime.now())
    is_admin = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)

    def to_dto(self):
        '''
        Given a User model object,
        builds and returns a User DTO object based on it.
        '''
        user_dto = User(user_id=self.id, social_id=self.social_id, name=self.name, email=self.email, avatar=self.avatar, creation_date=self.creation_date, is_admin=self.is_admin, is_active=self.is_active)
        return  user_dto

class Langs(base):
    '''
    SQLAlchemy model for langs table and Lang DTO objects.
    '''
    __tablename__ = "langs"
    id = Column(Integer, primary_key=True)
    lang_code = Column(String(5), unique=True, nullable=False)
    name = Column(String(200), nullable = False)
    is_active = Column(Boolean, nullable=False, default=True)

    def to_dto(self):
        '''
        Given a Langs model object,
        builds and returns a Lang DTO object based on it.
        '''
        lang_dto = Lang(lang_id=self.id, code=self.lang_code, name=self.name, is_active=self.is_active)
        return lang_dto

    def update(self, lang: Lang):
        '''
        Overwrites the attributes on the invoking Langs object
        based on another one passed as parameter.
        '''
        assert self.id == lang.id #ToDo; Manage this!
        self.lang_code = lang.lang_code
        self.name = lang.name
        self.is_active = lang.is_active


class Tags(base):
    '''
    SQLAlchemy model for tags table and Tag DTO objects.
    '''
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    tag = Column(String(50), nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=True)

    def to_dto(self):
        '''
        Given a Tags model object,
        builds and returns a Tag DTO object based on it.
        '''
        tag_dto=Tag(tag_id=self.id, tag=self.tag, is_active=self.is_active)
        return tag_dto

    def update(self, o_tag:'Tag'):
        '''
        Overwrites the attributes on the invoking Tags object
        based on another one passed as parameter.
        '''
        assert self.id==o_tag.id #ToDo: Manage this
        self.tag=o_tag.tag
        self.is_active=o_tag.is_active


class Statuses(base):
    '''
    SQLAlchemy model for status table and Status DTO objects.
    '''
    __tablename__ = "status"
    id = Column(Integer, primary_key=True)
    status = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    def to_dto(self):
        '''
        Given a Status model object,
        builds and returns a Status DTO object based on it.
        '''
        status_dto = Status(status_id=self.id, status=self.status, is_active=self.is_active)
        return status_dto

    def update(self, o_status: 'Status'):
        '''
        Overwrites the attributes of the invoking Status object,
        baed on another one passed as parameter.
        '''
        assert self.id==o_status.id     #ToDo: Manage this
        self.status=o_status.status
        self.is_active=o_status.is_active

class LangFormats(base):
    '''
    SQLAlchemy model for langformats table and LangFormat DTO objects.
    '''
    __tablename__ = "langformats"
    id = Column(Integer, primary_key=True)
    lang_format = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    def to_dto(self):
        '''
        Given a LangFormat model object,
        builds and returns a LangFormat DTO object based on it.
        '''
        langformat_dto = LangFormat(format_id=self.id, lang_format=self.lang_format, is_active=self.is_active)
        return langformat_dto

    def update(self, langformat:'LangFormat'):
        '''
        Overwrites the attributes of the invoking LangFormats object,
        based on another one passed as parameter.
        '''
        assert self.id == langformat.id #Todo: Manage this
        self.lang_format=langformat.lang_format
        self.is_active=langformat.is_active

class FileFormats(base):
    '''
    SQLAlchemy model for fileformats table and FileFormat DTO objects.
    '''
    __tablename__ = "fileformats"
    id = Column(Integer, primary_key=True)
    file_format = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    def to_dto(self):
        '''
        Given a Fileformat model object,
        builds and returns a FileFormat DTO object baed on it.
        '''
        fileformat_dto = FileFormat(format_id=self.id, file_format=self.file_format, is_active=self.is_active)
        return fileformat_dto

    def update(self, fileformat:'FileFormat'):
        '''
        Overwrites the attributes of the invoking FileFormats object,
        based on another one passed as parameter.
        '''
        assert self.id == fileformat.id  #ToDo ; Manage this!
        self.file_format = fileformat.file_format
        self.is_active = fileformat.is_active
