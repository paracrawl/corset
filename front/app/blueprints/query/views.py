import namegenerator
from flask import Blueprint, render_template, send_file, redirect, request, url_for
from flask_login import current_user, login_required

from back.bo.base_corpus_bo import BaseCorpusBO
from back.bo.custom_corpus_bo import CustomCorpusBO
from back.bo.langs_bo import LangsBO
from back.bo.query_request_bo import QueryRequestBO
from back.bo.tags_bo import TagsBO
from front.app import app
from front.app.utils import utils
from front.app.utils.user_utils import user_login_enabled

query_blueprint = Blueprint('query', __name__, template_folder='templates')


@query_blueprint.route('/')
@utils.condec(login_required, user_login_enabled())
def query_view():
    random_name = " ".join(namegenerator.gen().split("-")[:2])

    langs_bo = LangsBO()
    langs = langs_bo.get_langs()
    target_langs = [lang for lang in langs if lang.code != 'en']
    source_lang = langs_bo.get_lang_by_code('en')

    source_langs_codes = app.config['SOURCE_LANGS']
    source_langs = [lang for lang in langs if lang.code in source_langs_codes]

    base_corpus_bo = BaseCorpusBO()

    base_corpus = base_corpus_bo.get_base_corpora_by_pair('en', target_langs[0].code)[0]
    corpus_collection = base_corpus.solr_collection

    tags_bo = TagsBO()
    topics = tags_bo.get_tags()

    return render_template('query.html', active_page='query', title='Get corpora', langs=target_langs,
                           random_name=random_name, corpus_collection=corpus_collection, source_lang=source_lang,
                           source_langs=source_langs, topics=topics)


@query_blueprint.route('/download/<query_request_id>')
@utils.condec(login_required, user_login_enabled())
def query_download(query_request_id):
    try:
        query_request_id = int(query_request_id)

        query_request_bo = QueryRequestBO()
        query_request = query_request_bo.get_query_request(query_request_id)

        if query_request and query_request.status.status == 'SUCCESS' \
                and query_request.custom_corpus and query_request.custom_corpus.location \
                and (current_user.is_admin
                     or query_request.owner.user_id == current_user.id
                     or query_request.custom_corpus.is_private is False):
            custom_corpus_bo = CustomCorpusBO()
            custom_corpus_bo.update_custom_corpus_downloads(query_request.custom_corpus.corpus_id)
            return send_file(query_request.custom_corpus.location, as_attachment=True)
        else:
            raise ValueError()
    except ValueError:
        return redirect(request.referrer if request.referrer else url_for('search.search_view'))


@query_blueprint.route('/share/<query_request_id>')
@utils.condec(login_required, user_login_enabled())
def query_share(query_request_id):
    try:
        query_request_id = int(query_request_id)

        query_request_bo = QueryRequestBO()
        query_request = query_request_bo.get_query_request(query_request_id)

        if query_request and query_request.status.status == 'SUCCESS' \
                and query_request.custom_corpus and query_request.owner.user_id == current_user.id:
            status = query_request.custom_corpus.is_private
            custom_corpus_bo = CustomCorpusBO()
            custom_corpus_bo.toggle_custom_corpus_private(query_request.custom_corpus.corpus_id, not status)
            return redirect(request.referrer)
        else:
            raise ValueError()
    except ValueError:
        return redirect(request.referrer if request.referrer else url_for('search.search_view'))


@query_blueprint.route('/remove/<query_request_id>', methods=['GET', 'POST'])
@utils.condec(login_required, user_login_enabled())
def query_active(query_request_id):
    try:
        query_request_id = int(query_request_id)
        query_request_bo = QueryRequestBO()
        query_request = query_request_bo.get_query_request(query_request_id)

        if query_request and query_request.status.status == 'SUCCESS' \
                and query_request.custom_corpus \
                and (query_request.owner.user_id == current_user.id or current_user.is_admin):

            if request.method == 'POST':
                custom_corpus_bo = CustomCorpusBO()
                custom_corpus_bo.toggle_custom_corpus_active(query_request.custom_corpus.corpus_id,
                                                             active=False)
                return redirect(url_for('dashboard.dashboard_view'))
            else:
                return render_template('query-remove.html', active_page='query', title='Remove Corset',
                                       query_request=query_request)
        else:
            raise ValueError()
    except ValueError:
        return redirect(request.referrer if request.referrer else url_for('search.search_view'))
