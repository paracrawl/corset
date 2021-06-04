# Some utils to interact with user data

from flask_login import current_user
from front.app import app


def get_uid():
    if user_login_enabled() and current_user.is_authenticated:
        return current_user.id
    return None


def get_user():
    if user_login_enabled() and current_user and current_user.get_id() is not None:
        return current_user
    return None


def user_login_enabled():
    return app.config["USER_LOGIN_ENABLED"] if "USER_LOGIN_ENABLED" in app.config else False


def is_admin():
    user = get_user()
    return user.is_admin if user else False
