from sqlalchemy.sql import or_, and_
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text, inspect


from back.dto.query_corpus  import QueryCorpus

from back.bo.langs_bo import LangsBO

from back.models import QueryCorpora, Langs, FileFormats, LangFormats
from back.config import Config

from back.utils import *

class QueryCorpusBO:
    '''
    Business Objects for BaseCorpus DTO objects
    '''
    Session = sessionmaker(Config.db)
    session = Session()


    def add_query_corpus(self, new_corpus: QueryCorpus):
        '''
        Adds a new QueryCorpus to the system. 
        '''
        try:
            new_corpus_model = new_corpus.to_model()
            self.session.add(new_corpus_model)
            self.session.commit()
            ret = new_corpus_model.to_dto()  #according to doc, now corpus has its id updated
            self.session.close()
            return ret
        except IntegrityError as ex:
            #Error: Already existing in DB            
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.add_query_corpus.__name__, ex)
            logging.exception(msg)
            raise AlreadyExisting(msg) from None
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.add_query_corpus.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            
            

    def get_query_corpus(self, corpus_id: int):            
        '''
        Retrieves the metadata of a given QueryCorpus
        '''
        try:
            l1=aliased(Langs)
            #l2=aliased(Langs)
            model=self.session.query(QueryCorpora, l1, FileFormats, LangFormats).filter(QueryCorpora.id==corpus_id, l1.id==QueryCorpora.source_lang,  QueryCorpora.file_format==FileFormats.id, QueryCorpora.lang_format==LangFormats.id).first()
            if model == None:
                return None
            corpus=model[0].to_dto()
            src_lang=model[1].to_dto()
            fileformat=model[2].to_dto()
            langformat=model[3].to_dto()
            trg_lang=None
            if corpus.target_lang != None:
                #it was parallel
                #napa!
                lang_bo=LangsBO()
                trg_lang = lang_bo.get_lang(lang_id=corpus.target_lang)
            corpus.source_lang=src_lang
            corpus.target_lang=trg_lang
            corpus.file_format=fileformat
            corpus.lang_format=langformat
            self.session.close()
            return corpus
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_query_corpus.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None


    def get_available_query_corpora(self, include_inactive=False, limit=None, offset=0, sort_field="id", sort_dir="asc"):
        '''
        Retrieves the list of all available active QueryCorpus (if include_inactive, include those that are inactive as well)
        '''
        try:
            order = text(QueryCorpora.__tablename__ +"."+sort_field+" "+sort_dir)
            l1 = aliased(Langs)
            #l2 = aliased(Langs)

            if include_inactive:
                corpora_model_array = self.session.query(QueryCorpora, l1, FileFormats, LangFormats).filter(l1.id==QueryCorpora.source_lang, QueryCorpora.file_format==FileFormats.id, QueryCorpora.lang_format==LangFormats.id).order_by(order).offset(offset).limit(limit)
            else:
                corpora_model_array = self.session.query(QueryCorpora, l1, FileFormats, LangFormats).filter(l1.id==QueryCorpora.source_lang, QueryCorpora.file_format==FileFormats.id, QueryCorpora.lang_format==LangFormats.id, QueryCorpora.is_active==True).order_by(order).offset(offset).limit(limit)
                
            ret = build_query_corpora_array(corpora_model_array)
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_available_query_corpora.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None


    def toggle_query_corpus_active(self, corpus_id: int, active: bool):
        '''
        Marks a given QueryCorpus as active/not active.
        '''
        try:
            corpus = self.session.query(QueryCorpora).get(corpus_id)
            corpus.is_active = active
            self.session.commit()
            ret = corpus.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.toggle_query_corpus_active.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None

def build_query_corpora_array(resp):
    '''
    Given a array of QueryCorpora model objects,
    returns a array of QueryCorpus DTO objects.
    '''
    corpora=[]
    for model in resp:
        corpus = model[0].to_dto()
        src_lang = model[1].to_dto()
        fileformat = model[2].to_dto()
        langformat = model[3].to_dto()
        trg_lang=None
        if corpus.target_lang != None:
            #it was parallel
            #napa!
            lang_bo=LangsBO()
            trg_lang = lang_bo.get_lang(lang_id=corpus.target_lang)
        corpus.source_lang = src_lang
        corpus.target_lang = trg_lang
        corpus.file_format = fileformat
        corpus.lang_format = langformat
        corpora.append(corpus)
    return corpora

