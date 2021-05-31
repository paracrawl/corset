from flask import Blueprint, render_template, redirect, request, url_for, escape
from flask_login import current_user, login_required

from back.bo.base_corpus_bo import BaseCorpusBO
from back.bo.custom_corpus_bo import CustomCorpusBO
from back.bo.langs_bo import LangsBO
from back.bo.query_request_bo import QueryRequestBO
from back.bo.search_request_bo import SearchRequestBO
from front.app.utils.user_utils import user_login_enabled
from front.app import app, login_manager
from front.app.utils import utils

search_blueprint = Blueprint('search', __name__, template_folder='templates')


@search_blueprint.route('/')
@search_blueprint.route('/<corpus_collection>')
@search_blueprint.route('/<corpus_collection>/<lang>/<query>')
@utils.condec(login_required, user_login_enabled())
def search_view(corpus_collection=None, lang=None, query=''):
    langs_bo = LangsBO()
    langs = langs_bo.get_langs()
    target_langs = [lang for lang in langs if lang.code != 'en']

    base_corpus_bo = BaseCorpusBO()

    base_corpus = None
    source_lang = None
    target_lang = None
    field = 'trg'

    if corpus_collection:
        base_corpus = base_corpus_bo.get_base_corpus_by_collection(corpus_collection)
        source_lang = base_corpus.source_lang
        target_lang = base_corpus.target_lang
        field = 'trg' if target_lang.code == lang else 'src'
    else:
        base_corpus = base_corpus_bo.get_base_corpora_by_pair('en', target_langs[0].code)[0]
        corpus_collection = base_corpus.solr_collection
        source_lang = langs_bo.get_lang_by_code('en')

    return render_template('search.html', title='Search', active_page='search', langs=langs,
                           query=query, field=field, source_lang=source_lang,
                           target_lang=target_lang, corpus_collection=corpus_collection, base_corpus=base_corpus)


@search_blueprint.route('/', methods=['POST'])
@utils.condec(login_required, user_login_enabled())
def search_post():
    source_lang_id = int(request.form.get('source_lang'))
    target_lang_id = int(request.form.get('target_lang'))
    field = request.form.get('field')
    query = escape(request.form.get('queryText'))

    base_corpus_bo = BaseCorpusBO()
    base_corpus = base_corpus_bo.get_base_corpora_by_pair(source_lang_id, target_lang_id)[0]

    langs_bo = LangsBO()
    source_lang = langs_bo.get_lang(source_lang_id)
    target_lang = langs_bo.get_lang(target_lang_id)

    return redirect(url_for('search.search_view', corpus_collection=base_corpus.solr_collection,
                            lang=(target_lang.code if field == 'trg' else source_lang.code),
                            query=query))


@search_blueprint.route('/corset/<query_request_id>')
@search_blueprint.route('/corset/<query_request_id>/<lang>/<query>')
@utils.condec(login_required, user_login_enabled())
def search_corset(query_request_id, lang=None, query=None):
    query_request_bo = QueryRequestBO()
    query_request = query_request_bo.get_query_request(query_request_id)

    if query_request and query_request.custom_corpus:
        if query_request.owner.user_id == current_user.id or query_request.custom_corpus.is_private is False\
                or current_user.is_admin:
            source_lang = query_request.custom_corpus.source_lang
            target_lang = query_request.custom_corpus.target_lang
            field = 'trg' if query_request.custom_corpus.target_lang.code == lang else 'src'

            return render_template('search-corset.html', title='Preview corset', active_page='search',
                                   query=query, field=field, source_lang=source_lang, target_lang=target_lang,
                                   query_request_id=query_request.request_id, query_request=query_request,
                                   corset_id=query_request.custom_corpus.corpus_id)
        else:
            return redirect(request.referrer if request.referrer else url_for('search.search_view'))
    else:
        return redirect(request.referrer if request.referrer else url_for('search.search_view'))


@search_blueprint.route('/corset', methods=['POST'])
@utils.condec(login_required, user_login_enabled())
def search_corset_post():
    query_request_id = int(request.form.get('query_request_id'))
    field = request.form.get('field')
    query = escape(request.form.get('queryText'))

    query_request_bo = QueryRequestBO()
    query_request = query_request_bo.get_query_request(query_request_id)

    source_lang = query_request.custom_corpus.source_lang
    target_lang = query_request.custom_corpus.target_lang

    return redirect(url_for('search.search_corset', query_request_id=query_request.request_id,
                            lang=(target_lang.code if field == 'trg' else source_lang.code),
                            query=query))


@search_blueprint.route('/history/remove/<id>')
@utils.condec(login_required, user_login_enabled())
def history_remove(id):
    id = int(id)

    search_request_bo = SearchRequestBO()

    if id == 'all':
        search_request_bo.clear_user_search_history(current_user.id)
    else:
        user_search_requests = search_request_bo.get_user_search_requests(user_id=current_user.id)
        user_search_requests_ids = [search_request.search_id for search_request in user_search_requests]

        if id in user_search_requests_ids:
            search_request_bo.remove_search_history_entry(id)

    return redirect(request.referrer)
