from flask import Blueprint, render_template, request, url_for, redirect, escape
from flask_login import login_required, current_user

from back.bo.search_request_bo import SearchRequestBO
from front.app.utils import utils, user_utils
from models.user import User

from models.database import db

settings_blueprint = Blueprint('settings', __name__, template_folder='templates')


@settings_blueprint.route('/', methods=['GET'])
@utils.condec(login_required, user_utils.user_login_enabled())
def settings_view():
    search_request_bo = SearchRequestBO()
    history = search_request_bo.get_user_search_requests(current_user.id, sort_field='creation_date', sort_dir='desc')
    return render_template('settings.html', title='Settings', history=history)


@settings_blueprint.route('/', methods=['POST'])
@utils.condec(login_required, user_utils.user_login_enabled())
def settings_view_post():
    user = User.query.filter_by(id=user_utils.get_uid()).first()
    name = request.form.get('nameText')

    if name:
        user.name = escape(name)

    db.session.commit()

    return redirect(url_for('settings.settings_view'))
