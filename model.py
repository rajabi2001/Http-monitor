import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import jwt

db = SQLAlchemy()


class Model_Back():

    def __init__(self, app):
        self.app = app

    def SQLAlchemy_model(self):
        global db
        db.init_app(self.app)
        return db


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())

    def __init__(self, username, password, insert=False):
        self.username = username
        self.password = password

        if insert == True:
            db.session.add(self)
            db.session.commit()

    @classmethod
    def current_user(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def current_user_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def encode_auth_token(self, app):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
                'id': self.id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY')
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token, app):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get(
                'SECRET_KEY'),  algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class Url(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    address = db.Column(db.String(100), nullable=False)
    threshold = db.Column(db.Integer, nullable=False)
    failed_times = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())

    def __init__(self, address, threshold, user_id, insert=False):
        self.address = address
        self.threshold = threshold
        self.user_id = user_id

        if insert == True:
            db.session.add(self)
            db.session.commit()

    @classmethod
    def current_url(cls, current_user_id):
        return cls.query.filter_by(user_id=current_user_id).all()

    @classmethod
    def get_url(cls, url_id):
        return cls.query.filter_by(id=url_id).first()

    @classmethod
    def overthreshold(cls):
        return cls.query.filter(cls.failed_times >= cls.threshold).all()

    def get_url_data(self):
        url_data = {}
        url_data['id'] = self.id
        url_data['address'] = self.address
        url_data['threshold'] = self.threshold
        return url_data


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url_id = db.Column(db.Integer, db.ForeignKey('url.id'), nullable=False)
    result = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())

    def __init__(self, url_id, result):
        self.url_id = url_id
        self.result = result

    @classmethod
    def get_requests(cls, url_id):
        return cls.query.filter_by(url_id=url_id).all()

    def get_request_data(self):
        req_data = {}
        url = Url.get_url(self.url_id)
        req_data['url'] = url.address
        req_data['result'] = self.result
        req_data['created_at'] = self.created_at
        return req_data
