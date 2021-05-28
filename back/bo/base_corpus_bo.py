from sqlalchemy.sql import or_, and_
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text, inspect

from back.bo.langs_bo import LangsBO
from back.dto.base_corpus  import BaseCorpus

from back.bo.search_bo import SearchBO

from back.models import BaseCorpora
from back.models import Langs
from back.config import Config

from back.utils import *

class BaseCorpusBO:
    '''
    Business Objects for BaseCorpus DTO objects
    '''
    Session = sessionmaker(Config.db)
    session = Session()


    def get_available_base_corpora(self, include_inactive=False, limit=None, offset=0, sort_field="id", sort_dir="asc"):
        '''
        Retrieves the list of all available active BaseCorpus (if include_inactive, include those that are inactive as well)
        '''
        try:
            order = text(BaseCorpora.__tablename__ +"."+sort_field+" "+sort_dir)
            l1 = aliased(Langs)
            l2 = aliased(Langs)
      
            if include_inactive:
                corpora_model_array = self.session.query(BaseCorpora, l1, l2).filter(l1.id==BaseCorpora.source_lang, l2.id==BaseCorpora.target_lang).order_by(order).offset(offset).limit(limit)
            else:
                corpora_model_array = self.session.query(BaseCorpora, l1, l2).filter(l1.id==BaseCorpora.source_lang, l2.id==BaseCorpora.target_lang, BaseCorpora.is_active==True).order_by(order).offset(offset).limit(limit)
            ret = build_base_corpora_array(corpora_model_array)
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_available_base_corpora.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None


    def get_available_base_corpora_highlights(self, include_inactive=False, limit=None, offset=0, sort_field="id", sort_dir="asc"):
        '''
        Retrieves the list of all highlighted (promoted) BaseCorpus
        '''
        try:
            order = text(BaseCorpora.__tablename__+"."+sort_field+" "+sort_dir)
            l1=aliased(Langs)
            l2=aliased(Langs)
            if include_inactive:
                corpora_model_array = self.session.query(BaseCorpora, l1, l2).filter(l1.id==BaseCorpora.source_lang, l2.id==BaseCorpora.target_lang, BaseCorpora.is_highlight==True).order_by(order).offset(offset).limit(limit)
            else:
                corpora_model_array = self.session.query(BaseCorpora, l1, l2).filter(l1.id==BaseCorpora.source_lang, l2.id==BaseCorpora.target_lang, BaseCorpora.is_highlight==True, BaseCorpora.is_active==True).order_by(order).offset(offset).limit(limit)
            ret = build_base_corpora_array(corpora_model_array)
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_available_base_corpora_highlights.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
        
        

    def add_base_corpus(self, new_corpus: BaseCorpus):
        '''
        Adds a new BaseCorpus to the system. The corpus must be added to Solr by hand.
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
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.add_base_corpus.__name__, ex)
            logging.exception(msg)            
            raise AlreadyExisting(msg) from None
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.add_base_corpus.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None    



    def get_base_corpus(self, corpus_id: int):
        '''
        Retrieves the metadata of a given BaseCorpus
        '''
        try:
            l1=aliased(Langs)
            l2=aliased(Langs)
            model=self.session.query(BaseCorpora, l1, l2).filter(l1.id==BaseCorpora.source_lang, l2.id==BaseCorpora.target_lang, BaseCorpora.id==corpus_id).first()     
            if model == None:
                return None
            corpus=model[0].to_dto()
            src_lang=model[1].to_dto()
            trg_lang=model[2].to_dto()
            corpus.source_lang=src_lang
            corpus.target_lang=trg_lang
            self.session.close()
            return corpus
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_base_corpus.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None


    def get_collection(self, corpus_id: int):
        '''
        Retrieves the collection name of a given BaseCorpus.
        '''
        try:
            model = self.session.query(BaseCorpora).get(corpus_id)
            if model == None:
                return None
            corpus = model.to_dto()
            return corpus.solr_collection
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_collection.__name__, ex)      
            logging.exception(msg)
            raise UnknownError(msg) from None


    def get_base_corpus_by_collection(self, collection: str):
        '''
        Retrieves the metadata of a BaseCorpus, given it's Solr collection name
        '''
        try:
            l1=aliased(Langs)
            l2=aliased(Langs)
            model=self.session.query(BaseCorpora, l1, l2).filter(l1.id==BaseCorpora.source_lang, l2.id==BaseCorpora.target_lang, BaseCorpora.solr_collection==collection).first()
            if model == None:
                return None
            corpus=model[0].to_dto()
            src_lang=model[1].to_dto()
            trg_lang=model[2].to_dto()
            corpus.source_lang=src_lang
            corpus.target_lang=trg_lang
            self.session.close()
            return corpus
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_base_corpus_by_collection.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
    

    def get_base_corpus_preview(self, corpus_id, corpus=None, rows=100, start=0):
        '''
        Retrieves a sample of sentences from Solr for a given corpus (implies Solr query).
        '''        
        try:
            if corpus==None:
                corpus = self.get_base_corpus(corpus_id)
            search_bo = SearchBO()
            return search_bo.preview(corpus, rows, start)            
        except Exception as ex:
            raise ex #Keep raising the thing (chained)
        
             



    def modify_base_corpus(self, modified_corpus: BaseCorpus):
        '''
        Changes BaseCorpus metadata (name, description, etc)
        '''
        try:
            modified_corpus_model = modified_corpus.to_model()
            #ident = modified_corpus.id
            old_corpus_model = self.session.query(BaseCorpora).get(modified_corpus_model.id)
            old_corpus_model.update(modified_corpus_model) #The update function asserts the id is the same
            self.session.commit()
            ret = old_corpus_model.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.modify_base_corpus.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            


    def get_base_corpora_by_pair(self, lang1, lang2, include_inactive=False, limit=None, offset=0, sort_field="id", sort_dir="asc"):
        '''
        Retrieves a list of active BaseCorpus having a given language pair (src-trg OR trg-src).
        '''
        try:
            if type(lang1) == str and type(lang2) == str:
                langs_bo = LangsBO()
                lang1 = langs_bo.get_lang_by_code(lang1).lang_id
                lang2 = langs_bo.get_lang_by_code(lang2).lang_id
                
            order = text(BaseCorpora.__tablename__+"."+sort_field+" "+sort_dir)
            l1 = aliased(Langs)
            l2 = aliased(Langs)
            if include_inactive:        
                corpora_model_array = self.session.query(BaseCorpora, l1, l2)\
                    .filter(l1.id == BaseCorpora.source_lang, l2.id == BaseCorpora.target_lang,
                            or_(and_(BaseCorpora.source_lang == lang1, BaseCorpora.target_lang == lang2),
                                and_(BaseCorpora.source_lang == lang2, BaseCorpora.target_lang == lang1)))\
                    .order_by(order).offset(offset).limit(limit)
            else:
                corpora_model_array = self.session.query(BaseCorpora, l1, l2).filter(l1.id==BaseCorpora.source_lang, l2.id==BaseCorpora.target_lang, 
                or_(and_(BaseCorpora.source_lang==lang1, BaseCorpora.target_lang==lang2), and_(BaseCorpora.source_lang==lang2, BaseCorpora.target_lang==lang1))).filter(BaseCorpora.is_active==True).order_by(order).offset(offset).limit(limit)
            ret = build_base_corpora_array(corpora_model_array)
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_base_corpora_by_pair.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            
            
    def toggle_base_corpus_highlight(self, corpus_id: int, highlight: bool):
        '''
        Marks a given BaseCorpus as highlighted/not highlighted.
        '''
        try:
            corpus = self.session.query(BaseCorpora).get(corpus_id)
            corpus.is_highlight = highlight
            self.session.commit()
            ret = corpus.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.toggle_base_corpus_highlight.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            

    def toggle_base_corpus_active(self, corpus_id: int, active: bool):
        '''
        Marks a given BaseCorpus as active/not active.
        '''
        try:
            corpus = self.session.query(BaseCorpora).get(corpus_id)
            corpus.is_active = active
            self.session.commit()
            ret = corpus.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.toggle_base_corpus_active.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None

def build_base_corpora_array(resp):
    '''
    Given a array of BaseCorpora model objects,
    returns a array of BaseCorpus DTO objects.
    '''
    corpora=[]
    for model in resp:
        corpus_model = model[0]
        src_lang_model = model[1]
        trg_lang_model = model[2]
        corpus = corpus_model.to_dto()
        src_lang = src_lang_model.to_dto()
        trg_lang = trg_lang_model.to_dto()
        corpus.source_lang = src_lang
        corpus.target_lang = trg_lang 
        corpora.append(corpus)
    return corpora
