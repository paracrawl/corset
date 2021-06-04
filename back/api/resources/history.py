from flask_login import login_required, current_user
from flask_restx import Resource, reqparse

from back.bo.search_request_bo import SearchRequestBO
from back.dto.search_request import SearchRequest


class History(Resource):

    @login_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int, required=False,
                            help='Amount of history items to return')
        args = parser.parse_args(strict=True)

        search_request_bo = SearchRequestBO()
        history = search_request_bo.get_user_search_requests(current_user.id, sort_field='creation_date',
                                                             sort_dir='desc', limit=args['limit'])

        if history:
            return SearchRequest.schema().dump(history, many=True), 200
        else:
            return [], 404
