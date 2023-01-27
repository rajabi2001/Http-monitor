from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps
import re
import http_request
import threading
import schedule
import uuid
from db import DB_Back
from model import Model_Back, User, Url, Request

app = Flask(__name__)
# app.debug = True
app.config['SECRET_KEY'] = uuid.uuid4().hex

db_mysql = DB_Back(host='localhost', port='3306',
                   user="root", password="root", db_name="mytest")

app.config['SQLALCHEMY_DATABASE_URI'] = db_mysql.get_db_url()

mymodel = Model_Back(app)
db = mymodel.SQLAlchemy_model()


@app.route('/users', methods=['POST'])
def sign_up():

    data = request.form
    username = data.get('username')
    password = data.get('password')

    if not User.current_user(username):

        user = User(
            username=username,
            password=password,
            insert=True
        )

        token = user.encode_auth_token(app)

        return make_response(jsonify({
            'token': token,
            'message': "Successfully registered."}), 201)
    else:

        return make_response('Please Log in, User already exists.', 202)


@app.route('/users/login', methods=['POST'])
def login():

    data = request.form
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="Login required !!"'}
        )

    myuser = User.current_user(username)
    if not myuser:

        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'}
        )
    elif myuser.password == password:
        token = myuser.encode_auth_token(app)
        return make_response(jsonify({'token': token}), 201)

    return make_response(
        'Could not verify',
        403,
        {'WWW-Authenticate': 'Basic realm ="Wrong Password !!"'}
    )


def tokenify(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if 'x-access-token' in request.headers or request.headers['x-access-token'] != None:
            token = request.headers['x-access-token']
        else:
            return jsonify({'message': 'Token is missing !!'}), 401

        try:
            data = User.decode_auth_token(token, app)
            current_user = User.current_user_by_id(data['id'])

        except Exception as err:
            return jsonify({'message': 'Token is invalid !!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/urls', methods=['POST', 'GET'])
@tokenify
def urls(current_user):
    if request.method == 'POST':

        data = request.form
        address = data.get('address')
        threshold = data.get('threshold')

        Url(address, threshold, current_user.id, insert=True)
        return jsonify({'message': 'url has been added successfully.'}), 201
    else:
        urls = Url.current_url(current_user.id)
        return jsonify({'urls': [url.get_url_data() for url in urls]})


@app.route('/urls/<url_id>', methods=['GET'])
@tokenify
def url_requests(current_user, url_id):

    requests = Request.get_requests(url_id)
    return jsonify({'log': [request.get_request_data() for request in requests]})


@app.route('/alerts', methods=['GET'])
@tokenify
def alerts(current_user):

    urls = Url.overthreshold()
    response = {'failed_urls': [url.address for url in urls]}

    if (len(urls) != 0):
        response['alert_message'] = 'Url(s) has reached maximum failure.'

    return jsonify(response), 201


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def run_app():
    app.run()


if __name__ == "__main__":
    threading.Thread(target=run_app).start()

    schedule.every(5).seconds.do(run_threaded, db_mysql.periodic_request)
    while 1:
        schedule.run_pending()
