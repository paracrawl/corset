import requests
from flask import render_template, url_for, redirect, request, Response
from flask_login import current_user
from models.user import User

from . import app, login_manager
from .utils import user_utils, utils
from .utils.user_utils import user_login_enabled

# If we want to use a method in our templates, we must include it like this:
app.jinja_env.globals.update(**{
    "int": int,
    "len": len,
    "get_user": user_utils.get_user,
    "infix": app.config['INFIX'],
    "enumerate": enumerate,
    "is_admin": user_utils.is_admin,
})


# This is the user loader. It returns a User object given a user ID
@login_manager.user_loader
@utils.condec(login_manager.user_loader, user_login_enabled())
def load_user(user_id):
    return User.query.filter_by(social_id=user_id).first()


# @app.context_processor
# def base_template():
#     topics = app.config['TOPICS']
#
#     return dict(topics=topics)


@app.route('/')
@app.route('/index')
def index():
    # We can redirect to different views depending on whether the user is
    # logged in or not
    if current_user.is_authenticated:
        # In redirections, we use the qualified name of the function which renders the view
        # we want to redirec to.
        # We want to redirect to /home, which is rendered by the function home.
        # So we say:
        return redirect(url_for('search.search_view'))

    return render_template('index.html')


@app.route('/api/<path:path>', methods=['GET', 'POST'])
def api_proxy(path):
    api_url = app.config['API_URL']
    url = '{}/{}'.format(api_url, path)

    params = {key: value for key, value in request.args.items()}
    data = {key: value for key, value in request.form.items()}
    files = {key: value for key, value in request.files.items()}
    headers = {key: value for key, value in request.headers.items() if key != 'Content-Type'}

    response = None

    if request.method == 'GET':
        response = requests.get(url, headers=headers, params=params)
    elif request.method == 'POST':
        response = requests.post(url, headers=headers, data=data, files=files)

    return Response(
        response=response.content,
        status=response.status_code,
        headers=dict(response.headers)
    )
