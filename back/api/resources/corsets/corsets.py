from back.api.resources.filter_request import filter_request
from back.bo.base_corpus_bo import BaseCorpusBO
from back.bo.langs_bo import LangsBO
from back.dto.query_request import QueryRequest
from flask_login import login_required, current_user
from flask_restx import Resource, reqparse

from back.bo.query_request_bo import QueryRequestBO
from back.bo.user_bo import UserBO
from back.dto.sentence import Sentence


class Corsets(Resource):

    @login_required
    def get(self, query_request_id=None):
        query_request_bo = QueryRequestBO()

        if query_request_id:
            parser = reqparse.RequestParser()
            parser.add_argument('preview', type=bool, help='Return preview')
            parser.add_argument('preview_rows', type=int, help='Number of preview sentences')
            parser.add_argument('preview_start', type=int, help='Offset of preview sentences')
            args = parser.parse_args(strict=True)

            query_request = query_request_bo.get_query_request(query_request_id)

            if query_request and (query_request.owner.user_id == current_user.id or
                                  (query_request.custom_corpus and query_request.custom_corpus.is_private is False)
                                  or current_user.is_admin):

                query_request.owner = {'user_id': query_request.owner.user_id}

                if args['preview']:
                    response = {}

                    start = args['preview_start']
                    rows = args['preview_rows'] if args['preview_rows'] else 10
                    rows = rows if rows < 100 else 100

                    if query_request and query_request.custom_corpus:
                        response['query_request'] = QueryRequest.schema().dump(query_request)

                        base_corpus_bo = BaseCorpusBO()
                        preview_sentences = base_corpus_bo.get_base_corpus_preview(None, corpus=query_request.custom_corpus,
                                                                                   rows=rows, start=start)
                        response['preview_sentences'] = Sentence.schema().dump(preview_sentences, many=True)
                    else:
                        return '', 404

                    if response and response['query_request']:
                        return response, 200
                else:
                    return QueryRequest.schema().dump(query_request), 200
            else:
                return '', 404
        else:
            parser = reqparse.RequestParser()
            parser.add_argument('public', type=bool, required=False,
                                help='Return public corsets')
            args = parser.parse_args(strict=True)

            query_requests = []

            if args['public']:
                query_requests = query_request_bo.get_public_custom_corpora_requests(sort_dir="desc",
                                                                                     sort_field="creation_date")
            else:
                query_requests = query_request_bo.get_query_requests() if current_user.is_admin else []

            if query_requests:
                query_requests = [request for request in query_requests
                                  if request.custom_corpus is None or request.custom_corpus.is_active is True]

                for request in query_requests:
                    filter_request(request)

                return QueryRequest.schema().dump(query_requests, many=True), 200
            else:
                return [], 404

    @login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('base_corpus', type=int, required=True, help='ID of Base Corpus')
        parser.add_argument('query_corpus', type=int, required=True, help='ID of Query Corpus')

        return '', 500
