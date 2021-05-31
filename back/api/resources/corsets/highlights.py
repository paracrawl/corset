from back.api.resources.filter_request import filter_request
from back.dto.query_request import QueryRequest

from back.bo.query_request_bo import QueryRequestBO
from flask_login import login_required
from flask_restx import Resource


class Highlights(Resource):

    @login_required
    def get(self):
        query_request_bo = QueryRequestBO()
        highlights = query_request_bo.get_popular_custom_corpora_requests(limit=5)

        if highlights:
            for request in highlights:
                filter_request(request)

            return QueryRequest.schema().dump(highlights, many=True), 200
        return [], 404
