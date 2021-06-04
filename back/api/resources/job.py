from back.api.resources.filter_request import filter_request
from back.bo.query_request_bo import QueryRequestBO
from back.dto.query_request import QueryRequest
from flask_login import login_required, current_user
from flask_restx import Resource, reqparse


class Job(Resource):

    @login_required
    def get(self, job_id=None):
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int, required=False,
                            help='Amount of requests to return')
        parser.add_argument('all', type=bool, required=False,
                            help='Return jobs for all users (only admin)')
        args = parser.parse_args(strict=True)

        if job_id:
            return '', 404
        else:
            query_request_bo = QueryRequestBO()
            pending_requests = []

            if not args['all']:
                pending_requests = query_request_bo\
                    .get_user_query_requests(current_user.id, sort_dir="desc",
                                             sort_field="creation_date",
                                             limit=args['limit'])
            elif current_user.is_admin:
                pending_requests = query_request_bo.get_query_requests(sort_dir="desc",
                                                                       sort_field="creation_date",
                                                                       limit=args['limit'])
            if pending_requests:
                pending_requests = [request for request in pending_requests
                                    if request.custom_corpus is None or request.custom_corpus.is_active is True]

                for request in pending_requests:
                    filter_request(request, is_admin=current_user.is_admin)

                return QueryRequest.schema().dump(pending_requests, many=True), 200
            else:
                return [], 404
