def filter_request(request, is_admin=False):
    if request.query_corpus:
        request.query_corpus.location = None

    if request.custom_corpus:
        request.custom_corpus.location = None

    if request.owner and not is_admin:
        request.owner = {'user_id': request.owner.user_id}
