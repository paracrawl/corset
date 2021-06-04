from flask import Blueprint, render_template
from flask_login import login_required

from front.app.utils import user_utils, utils

dashboard_blueprint = Blueprint('dashboard', __name__, template_folder='templates')


@dashboard_blueprint.route('/')
@utils.condec(login_required, user_utils.user_login_enabled())
def dashboard_view():
    return render_template('dashboard.html', title='Dashboard', active_page='dashboard')
