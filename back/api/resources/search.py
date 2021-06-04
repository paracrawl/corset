from datetime import datetime

from back.bo.base_corpus_bo import BaseCorpusBO
from back.bo.custom_corpus_bo import CustomCorpusBO
from back.bo.langs_bo import LangsBO
from back.bo.user_bo import UserBO
from back.dto.search_request import SearchRequest

from back.dto.search_response import SearchResponse
from flask_login import login_required, current_user
from flask_restx import Resource, reqparse

from back.bo.search_bo import SearchBO


class Search(Resource):

    @login_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('base_corpus', type=int, required=False,
                            help='ID of the Base Corpus to which perform the search')
        parser.add_argument('custom_corpus', type=int, required=False,
                            help='ID of the Custom Corpus to which perform the search')
        parser.add_argument('search_term', type=str, required=True, help='Search term')
        parser.add_argument('search_lang', type=str, required=False, help='Code of target search language')
        parser.add_argument('rows', type=int, required=True, help='Amount of sentences to return')
        parser.add_argument('field', type=str, required=True, help='Search in source or target')
        args = parser.parse_args(strict=True)

        rows = args['rows'] if args['rows'] < 50 else 50

        search_request: SearchRequest = None
        if args['base_corpus']:
            base_corpus_bo = BaseCorpusBO()
            base_corpus = base_corpus_bo.get_base_corpus(args['base_corpus'])

            search_request: SearchRequest = SearchRequest(None, UserBO().get_user(current_user.id), datetime.now(tz=None),
                                                          base_corpus, None, None,
                                                          'src' if args['field'] == 'src' else 'trg', args['search_term'],
                                                          'exact', rows, 0)
        elif args['custom_corpus']:
            custom_corpus_bo = CustomCorpusBO()
            custom_corpus = custom_corpus_bo.get_custom_corpus(args['custom_corpus'])

            search_request: SearchRequest = SearchRequest(None, UserBO().get_user(current_user.id), datetime.now(tz=None),
                                                          None, custom_corpus, None,
                                                          'src' if args['field'] == 'src' else 'trg', args['search_term'],
                                                          'exact', rows, 0)

        search_bo = SearchBO()
        search_response: SearchResponse = search_bo.search(search_request)

        if search_response:
            return SearchResponse.schema().dump(search_response), 200
        else:
            return [], 404
