def filter_request(request):
    if request.query_corpus:
        request.query_corpus.location = None

    if request.custom_corpus:
        request.custom_corpus.location = None

    if request.owner:
        request.owner = {'user_id': request.owner.user_id}
