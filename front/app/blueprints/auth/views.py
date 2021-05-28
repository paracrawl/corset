# This is a Blueprint! Think of it as a component.
# Every route you defined here will have a prefix, in this case, "/auth"
# It also has its own views file (this one) and its own template folder for
# jinja2 templates

import os

from flask_login import login_required, current_user, login_user, logout_user
from flask import Blueprint, flash, redirect, url_for
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.contrib.google import make_google_blueprint
from sqlalchemy.orm.exc import NoResultFound

from models.user import User, OAuth

from ... import app, db, login_manager
from ...utils import user_utils, utils


# Prefix is defined here!

auth_blueprint = Blueprint('auth', __name__, template_folder='templates')

# And now we use Flask-Dance to manage Google Auth login

if app.config['OAUTHLIB_INSECURE_TRANSPORT']:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

login_manager.login_view = 'google.login'
login_manager.login_message = ''


@auth_blueprint.route('/logout')
@utils.condec(login_required, user_utils.user_login_enabled())
def logout():
    logout_user()
    return redirect(url_for('index'))


google_blueprint = make_google_blueprint(
    scope=["openid",
           "https://www.googleapis.com/auth/userinfo.email",
           "https://www.googleapis.com/auth/userinfo.profile"])

if user_utils.user_login_enabled():
    app.register_blueprint(google_blueprint, url_prefix='/auth')
    google_blueprint.storage = SQLAlchemyStorage(OAuth, db.session, user=current_user)


@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(blueprint, token):
    account_info = blueprint.session.get(app.config['GOOGLE_USER_DATA_URL'])

    if account_info.ok:
        account_info_json = account_info.json()
        user_id = account_info_json['id']
        query = User.query.filter_by(social_id=user_id)

        try:
            user = query.one()
        except NoResultFound:
            if not app.config['ENABLE_NEW_LOGINS']:
                flash('New user logging is temporary disabled', "warning")
                return False
            user = User(social_id=user_id, name=account_info_json['name'], email=account_info_json['email'],
                        avatar=account_info_json['picture'], is_active=True)
            db.session.add(user)
            db.session.commit()

            print("New user created")

        # Update admins
        for i in app.config['ADMINS']:
            try:
                admin_user = User.query.filter(User.email == i).one()
                admin_user.is_admin = True
            except NoResultFound:
                pass

        db.session.commit()

        # Check bans
        if user.email in app.config['BANNED_USERS'] or not user.is_active:
            flash('User temporary banned')
            return False

        login_user(user)
        return True

    print("No account info available")
    return False
