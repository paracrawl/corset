from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from .database import db


class User(UserMixin, db.Model):
    __tablename__  = 'users'
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(140), unique=True, nullable=False)
    name = db.Column(db.String(250))
    email = db.Column(db.String(60), unique=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(250))

    def get_id(self):
        return self.social_id


# This is used by Flask-Dance (library for OAuth)
class OAuth(OAuthConsumerMixin, db.Model):
    __tablename__ = 'flask_dance_oauth'
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship('User')
