import pysolr
from requests.auth import HTTPBasicAuth


from back.dto.search_request  import SearchRequest
from back.dto.search_response import SearchResponse
from back.dto.corpus import Corpus
from back.dto.base_corpus import BaseCorpus
from back.dto.custom_corpus import CustomCorpus
from back.dto.sentence import Sentence

from back.bo.search_request_bo import SearchRequestBO 

from back.config import Config

from back.utils import *


class SearchResponseBO:
    '''
    Business Object for Search Responses
    '''
    request_bo = SearchRequestBO()

    def get_results(self, request: SearchRequest):
        '''
        Retrieves results for a given request
        '''
        try:
            response = self.query_solr(request) #actually does the search
            return response
        except Exception as ex:
            raise ex #Keep raising the thing
    
    def get_preview(self, corpus: Corpus, rows: int, start: int):
        '''
        Retrieves a sample from a corpus
        '''
        try:
            collection = corpus.solr_collection
            solr = pysolr.Solr(Config.SOLR_URI+"/"+collection, auth=HTTPBasicAuth(Config.SOLR_USR,Config.SOLR_PWD))
            if isinstance(corpus, BaseCorpus):
                solr_results = solr.search(q="*:*", rows=rows, start=start, sort="custom_score desc")
            else: #Is custom corpus
                print(corpus.solr_prefix)
                solr_results = solr.search(fq="id:{}.*".format(corpus.solr_prefix), q="*:*", rows=rows, start=start, sort="custom_score desc")
            sentences = build_sentences_array(solr_results, None, None)            
            return sentences
        except Exception as ex:
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.get_preview.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
        
    def query_solr(self, request: SearchRequest ):
        try:        
            is_custom = False
            if request.base_corpus != None:
                collection = request.base_corpus.solr_collection
            elif request.custom_corpus != None:
                is_custom = True
                collection = request.custom_corpus.solr_collection
                prefix = request.custom_corpus.solr_prefix
            else:
                return None                
            if request.search_type==None or request.search_type=="exact":
                search_str = "\""+request.search_term+"\""
            elif request.search_type=="partial":
                search_str = "*"+request.search_term+"*"
            elif request.search_type=="fuzzy":
                logging.warn("Warning: Fuzzy search still not supported. Fallback to exact search.")
                search_str = "\""+request.search_term+"\""
            else:
                logging.warn("Warning: Unknown search type \"{0}\". Fallback to exact search.".format(request.search_type))
                search_str = "\""+request.search_term+"\""       
            
            solr = pysolr.Solr(Config.SOLR_URI+"/"+collection, auth=HTTPBasicAuth(Config.SOLR_USR,Config.SOLR_PWD))
            if is_custom == False:
                solr_results = solr.search(q=request.search_field+":"+search_str, rows=request.rows, start=request.start, **{'hl':'true', 'hl.fl':request.search_field, 'hl.fragsize':'0'}, sort="custom_score desc")
            else:
                solr_results = solr.search(fq="id:{}.*".format(prefix), q=request.search_field+":"+search_str, rows=request.rows, start=request.start, **{'hl':'true', 'hl.fl':request.search_field, 'hl.fragsize':'0'}, sort="custom_score desc")    
            
            sentences = build_sentences_array(solr_results, solr_results.highlighting, request.search_field)            
            response = SearchResponse(request=request, occurrences = solr_results.hits, rows=request.rows, start=request.start, results=sentences)            
            return response
        except Exception as ex:
            msg = "{0} - {1} : {2}".format(self.__class__.__name__, self.query_solr.__name__, ex)
            logging.exception(msg)
            raise UnknownError(msg) from None
            

def build_sentences_array(results: pysolr.Results, highlights, search_field: str):
    sentences = []    
    highlights_keys = []

    if highlights != None:
        highlights_keys =  highlights.keys()
        
    for r in results:
        solr_id = r.get("id")
        source = r.get("src")
        target = r.get("trg")
        score = r.get("custom_score")
        tags = r.get("tags")  #Tags probably need to be turned into a proper list
        
        if solr_id in highlights_keys:
            if search_field =="src":
                source = highlights.get(solr_id).get(search_field)[0]
            if search_field == "trg":
                target = highlights.get(solr_id).get(search_field)[0]   
            
        s = Sentence(solr_id=solr_id, source=source, target=target, score=score, tags=tags)
        sentences.append(s)
    return sentences    
