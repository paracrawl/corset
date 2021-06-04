from back.dto.search_request  import SearchRequest
from back.dto.search_response import SearchResponse

from back.dto.corpus import Corpus

from back.bo.search_request_bo import SearchRequestBO
from back.bo.search_response_bo import SearchResponseBO

class SearchBO:
    '''
    Business Object for Searches
    '''

    request_bo = SearchRequestBO()
    response_bo = SearchResponseBO()

    def search(self, request: SearchRequest):
        '''
        Performs a search, given a Request, returning a Response
        '''
        try:

            response = self.response_bo.get_results(request) #actually does the search
            if request.base_corpus != None: #Custom corpus searches not being stored currently
                self.request_bo.add_search_request(request) #stores it in DB
            return response
        except Exception as ex:
            #keep raising the exception
            raise ex


    def preview(self, corpus: Corpus, rows=100, start=0):
        '''
        Retrieves a preview for a given Basecorpus.
        '''
        try:
            response = self.response_bo.get_preview(corpus, rows, start)
            return response
        except Exception as ex:
            raise ex #Raised chained    


        