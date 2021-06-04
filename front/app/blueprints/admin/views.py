import flask
import psutil as psutil

from back.bo.base_corpus_bo import BaseCorpusBO
from back.dto.base_corpus import BaseCorpus
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user, login_required

from back.bo.langs_bo import LangsBO
from front.app import app
from front.app.utils import utils, user_utils

admin_blueprint = Blueprint('admin', __name__, template_folder='templates')


@admin_blueprint.route('/')
@utils.condec(login_required, user_utils.user_login_enabled())
def admin_view():
    if not current_user.is_admin:
        return redirect(url_for('search.search_view'))

    factor = 1073741824
    vmem = psutil.virtual_memory()
    ram = {"percent": vmem.percent, "used": round(vmem.used / factor, 1), "total": round(vmem.total / factor, 1)}  # GB

    cpu = round(psutil.cpu_percent(), 2)
    hdd = psutil.disk_usage(app.config['BASEDIR'])
    disk_usage = {"percent": round((hdd.used / hdd.total) * 100, 1), "used": round(hdd.used / factor, 1),
                  "total": round(hdd.total / factor,1)}  # GB

    langs_bo = LangsBO()
    langs = langs_bo.get_langs()

    return render_template('admin.html', title='Admin', active_page='admin',
                           ram=ram, disk_usage=disk_usage, cpu=cpu, langs=langs)


@admin_blueprint.route('/add/base', methods=["POST"])
@utils.condec(login_required, user_utils.user_login_enabled())
def admin_add_base_corpora():
    if current_user.is_admin:
        name = request.form.get('corpusName')
        description = request.form.get('descriptionText')
        source_lang = int(request.form.get('sourceLang'))
        target_lang = int(request.form.get('targetLang'))
        solr_collection = request.form.get('solrCollection')

        # We do not trust user input
        name = flask.escape(name)
        description = flask.escape(description)
        solr_collection = flask.escape(solr_collection)

        # Base Corpus object
        base_corpus: BaseCorpus = BaseCorpus(name=name, description=description,
                                             source_lang=source_lang, target_lang=target_lang,
                                             solr_collection=solr_collection, is_active=True,
                                             is_highlight=False, corpus_id=None, sentences=0, size=0)

        base_corpus_bo = BaseCorpusBO()
        base_corpus_bo.add_base_corpus(base_corpus)
        return {'result': 200}
    else:
        return redirect(url_for('search.search_view'))
