from datetime import datetime
from typing import List
from collections import Counter
import cld3



from sqlalchemy.sql import or_, and_
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.exc import IntegrityError

from back.bo.tags_bo import TagsBO
from back.dto.custom_corpus import CustomCorpus

from back import Config, CustomCorpora, Langs, FileFormats
from back.utils import *


class CustomCorpusBO:
    '''
    Business Objects for CustomCorpus DTO objects
    '''
    Session = sessionmaker(Config.db)
    session = Session()

    def get_available_custom_corpora(self, include_inactive=False, limit=None,
                                     offset=0, sort_field="id", sort_dir="asc"):
        '''
        Retrieves the list of all available active CustomCorpus (if include_inactive, include those that are inactive as well)
        '''
        try:
            order = text(CustomCorpora.__tablename__ + "." + sort_field + " " + sort_dir)
            l1 = aliased(Langs)
            l2 = aliased(Langs)

            if include_inactive:
                corpora_model_array = self.session.query(CustomCorpora, l1, l2, FileFormats)\
                    .filter(l1.id == CustomCorpora.source_lang, l2.id == CustomCorpora.target_lang,
                            CustomCorpora.file_format == FileFormats.id)\
                    .order_by(order).offset(offset).limit(limit)
            else:
                corpora_model_array = self.session.query(CustomCorpora, l1, l2, FileFormats)\
                    .filter(l1.id == CustomCorpora.source_lang, l2.id == CustomCorpora.target_lang,
                            CustomCorpora.file_format == FileFormats.id,  CustomCorpora.is_active == True)\
                    .order_by(order).offset(offset).limit(limit)
            ret = build_custom_corpora_array(corpora_model_array)
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_available_custom_corpora.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None

    def get_available_custom_corpora_highlights(self, include_inactive=False, limit=None, offset=0, sort_field="id", sort_dir="asc"):
        '''
        Retrieves the list of all highlighted (promoted) CustomCorpora
        '''
        try:
            order = text(CustomCorpora.__tablename__+"."+sort_field+" "+sort_dir)
            l1=aliased(Langs)
            l2=aliased(Langs)
            if include_inactive:
                corpora_model_array = self.session.query(CustomCorpora, l1, l2, FileFormats).filter(l1.id==CustomCorpora.source_lang, l2.id==CustomCorpora.target_lang, FileFormats.id==CustomCorpora.file_format,
                                      CustomCorpora.is_highlight==True).order_by(order).offset(offset).limit(limit)
            else:
                corpora_model_array = self.session.query(CustomCorpora, l1, l2, FileFormats).filter(l1.id==CustomCorpora.source_lang, l2.id==CustomCorpora.target_lang, FileFormats.id==CustomCorpora.file_format,
                                     CustomCorpora.is_highlight==True, CustomCorpora.is_active==True).order_by(order).offset(offset).limit(limit)
            ret = build_custom_corpora_array(corpora_model_array)
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_available_custom_corpora_highlights.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None

    def get_custom_corpora_by_pair(self, lang1, lang2, limit=None, offset=0, sort_field="id", sort_dir="asc"):
        '''
        Retrieves a list of active CustomCorpus having a given language pair (src-trg OR trg-src).
        '''
        try:
            if type(lang1) == str and type(lang2) == str:
                langs_bo = LangsBO()
                lang1 = langs_bo.get_lang_by_code(lang1).lang_id
                lang2 = langs_bo.get_lang_by_code(lang2).lang_id
                
            order = text(CustomCorpora.__tablename__+"."+sort_field+" "+sort_dir)
            l1 = aliased(Langs)
            l2 = aliased(Langs)
            corpora_model_array = self.session.query(CustomCorpora, l1, l2, FileFormats).filter(l1.id==CustomCorpora.source_lang, l2.id==CustomCorpora.target_lang, 
                                or_(and_(CustomCorpora.source_lang==lang1, CustomCorpora.target_lang==lang2), and_(CustomCorpora.source_lang==lang2, CustomCorpora.target_lang==lang1)), FileFormats.id==CustomCorpora.file_format)\
                                .filter(CustomCorpora.is_active==True).order_by(order).offset(offset).limit(limit)
            ret = build_custom_corpora_array(corpora_model_array)
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_custom_corpora_by_pair.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None

    def get_custom_corpora_by_pair_and_topic(self, lang1, lang2, topic, limit=None, offset=0, sort_field="id", sort_dir="asc"):
        '''
        Retrieves a list of active CustomCorpus having a given language pair (src-trg OR trg-src) and topic.
        '''
        try:
            if type(lang1) == str and type(lang2) == str:
                langs_bo = LangsBO()
                lang1 = langs_bo.get_lang_by_code(lang1).lang_id
                lang2 = langs_bo.get_lang_by_code(lang2).lang_id

            order = text(CustomCorpora.__tablename__+"."+sort_field+" "+sort_dir)
            l1 = aliased(Langs)
            l2 = aliased(Langs)
            corpora_model_array = self.session.query(CustomCorpora, l1, l2, FileFormats).filter(l1.id==CustomCorpora.source_lang, l2.id==CustomCorpora.target_lang, 
                                or_(and_(CustomCorpora.source_lang==lang1, CustomCorpora.target_lang==lang2), and_(CustomCorpora.source_lang==lang2, CustomCorpora.target_lang==lang1)),
                                FileFormats.id==CustomCorpora.file_format, CustomCorpora.topics.any(topic))\
                                .filter(CustomCorpora.is_active==True).order_by(order).offset(offset).limit(limit)
            ret = build_custom_corpora_array(corpora_model_array)
            self.session.close()
            return ret
        except Exception as ex:
            self.session.close
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_custom_corpora_by_pair.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None



    def add_custom_corpus(self, new_corpus: CustomCorpus):
        '''
        Adds a new CustomCorpus to the system. 
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
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.add_custom_corpus.__name__, ex)
            logging.exception(msg)
            raise AlreadyExisting(msg) from None
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.add_custom_corpus.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None

    def get_custom_corpus(self, corpus_id: int):
        '''
        Retrieves the metadata of a given CustomCorpus
        '''
        try:
            l1=aliased(Langs)
            l2=aliased(Langs)
            model=self.session.query(CustomCorpora, l1, l2, FileFormats).filter(l1.id==CustomCorpora.source_lang, l2.id==CustomCorpora.target_lang, FileFormats.id==CustomCorpora.file_format, CustomCorpora.id==corpus_id).first()     
            if model == None:
                return None
            corpus = model[0].to_dto()
            src_lang = model[1].to_dto()
            trg_lang = model[2].to_dto()
            fileformat = model[3].to_dto()
            corpus.source_lang = src_lang
            corpus.target_lang = trg_lang
            corpus.file_format = fileformat

            tags_bo = TagsBO()
            corpus.topics = [tags_bo.get_tag(tag_id) for tag_id in corpus.topics]

            self.session.close()
            return corpus
        except Exception as ex:
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_custom_corpus.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None


    def toggle_custom_corpus_highlight(self, corpus_id: int, highlight: bool):
        '''
        Marks a given CustomCorpus as highlighted/not highlighted.
        '''
        try:
            corpus = self.session.query(CustomCorpora).get(corpus_id)
            corpus.is_highlight = highlight
            self.session.commit()
            ret = corpus.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.toggle_custom_corpus_highlight.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None

    def toggle_custom_corpus_active(self, corpus_id: int, active: bool):
        '''
        Marks a given CustomCorpus as active/not active.
        '''
        try:
            corpus = self.session.query(CustomCorpora).get(corpus_id)
            corpus.is_active = active
            self.session.commit()
            ret = corpus.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.toggle_custom_corpus_active.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None


    def toggle_custom_corpus_private(self, corpus_id: int, private: bool):
        '''
        Marks a given CustomCorpus as private/not private
        '''
        try:
            corpus = self.session.query(CustomCorpora).get(corpus_id)
            corpus.is_private = private
            self.session.commit()
            ret = corpus.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.toggle_custom_corpus_private.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None

    def update_custom_corpus_downloads(self, corpus_id:int):
        '''
        Updates the date of last_download a num_downloads.
        '''
        try:
            corpus = self.session.query(CustomCorpora).get(corpus_id)
            corpus.last_download = datetime.now()
            corpus.num_downloads = corpus.num_downloads + 1
            self.session.commit()
            ret = corpus.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.update_custom_corpus_downloads.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None

    def update_custom_corpus_name(self, corpus_id:int, new_name:str):
        '''
        Updates the name of a given custom corpus.
        '''
        try:
            corpus = self.session.query(CustomCorpora).get(corpus_id)
            corpus.name = new_name
            self.session.commit()
            ret = corpus.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.update_custom_corpus_name.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            
            
    def update_custom_corpus_topics(self, corpus_id:int, new_topics:List[int]):
        '''
        Updates the topics of a given custom corpus.
        '''
        try:
            corpus = self.session.query(CustomCorpora).get(corpus_id)
            corpus.topics = new_topics
            self.session.commit()
            ret = corpus.to_dto()
            self.session.close()
            return ret
        except Exception as ex:
            self.session.rollback()
            self.session.close()
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.update_custom_corpus_topics.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            
            
    def build_config_file(self, config_file, input, output, sents, collection, lang, side, lang2, side2, isparallel, outformat):    
        template="""input: {}
output: {}
sents: {}
collection: {}
lang: {}
side: {}
lang2: {}
side2: {}
isparallel: {}
outformat: {}
"""
        f = open(config_file, "w")
        
        f.write(template.format(input, output, sents, collection, lang, side, lang2, side2, isparallel, outformat))
        f.close()
        return
        
           



def build_custom_corpora_array(resp):
    '''
    Given a array of CustomCorpora model objects,
    returns a array of CustomCorpus DTO objects.
    '''
    corpora=[]
    for model in resp:
        corpus = model[0].to_dto()
        src_lang = model[1].to_dto()
        trg_lang = model[2].to_dto()
        fileformat = model[3].to_dto()
        corpus.source_lang = src_lang
        corpus.target_lang = trg_lang
        corpus.file_format = fileformat

        tags_bo = TagsBO()
        corpus.topics = [tags_bo.get_tag(tag_id) for tag_id in corpus.topics]

        corpora.append(corpus)
    return corpora


def identify_langs(src_sents, trg_sents, collection_src, collection_trg):
    '''
    Given a sample of sentences from source and target,
    and the source and target langs from the Solr collection to query,
    return [lang, side, lang2, side2, isparallel, reliable]
    '''
    reliable = True
    
    src_detected_array = []
    trg_detected_array = []
    
    if trg_sents==None or len(trg_sents)==0:
        isparallel=False
    else:
        isparallel=True    
    
    #LanguagePrediction(language='zh', probability=0.999969482421875, is_reliable=True, proportion=1.0)
    
    for sent in src_sents:
        if len(sent)<30:
            continue
        lang_pred = cld3.get_language(sent)
        if lang_pred.is_reliable:        
            src_detected_array.append(lang_pred.language)

    if isparallel:        
        for sent in trg_sents:
            if len(sent)<30:
                continue
            lang_pred = cld3.get_language(sent)
            if lang_pred.is_reliable:
                trg_detected_array.append(lang_pred.language)
    
    src_langmap = Counter(src_detected_array)
    if isparallel:
        trg_langmap = Counter(trg_detected_array)
    
    src_lang = src_langmap.most_common(1)[0][0]
    if isparallel:
        trg_lang = trg_langmap.most_common(1)[0][0]
    
    if src_langmap.most_common(1)[0][1] < len(src_sents)/2:
        reliable = False
    if isparallel:
        if trg_langmap.most_common(1)[0][1] < len(trg_sents)/2:
            reliable = False    

    
        

    if isparallel:
        if src_lang == collection_src and trg_lang == collection_trg:
            #best case, yay!
            return [collection_src, "src", collection_trg, "trg", isparallel, reliable]
        elif src_lang == collection_trg and trg_lang == collection_src:
            #src and trg langs swapped
            return [collection_trg, "trg", collection_src, "src", isparallel, reliable]
        else:
            #Failback    
            return [collection_src, "src", collection_trg, "trg", isparallel, False]
    else:
        if src_lang == collection_src:
            return [collection_src, "src", collection_trg, "trg", isparallel, reliable]
        elif src_lang == collection_trg:
            return [collection_trg, "trg", collection_src, "src", isparallel, reliable]
        else:
            return [collection_src, "src", collection_trg, "trg", isparallel, False]
   
            
            


    