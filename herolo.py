import os

from flask import Flask, request, session
from flask_pymongo import PyMongo

import authentication
from api_calls import Api
from db_connaction import DbConfig
from login_auth import LoginAuth

db = DbConfig()
app = Flask(__name__)
app.config["MONGO_DBNAME"] = db.db_name
app.config["MONGO_URI"] = db.db_connection
mongo = PyMongo(app)
api = Api(mongo)


@app.before_first_request
def update_user():
    api.user = session.get('username')


@app.route('/')
def start():
    return "App is on"


@app.route('/write_message', methods=['GET', 'POST'])
def write_message():
    quary = request.args
    auth = authentication.check_message_quary(quary)
    if auth == 'OK':
        api.write_message(quary)
        return 'Message send successfully'
    if auth != '':
        return 'Write message Failed {}'.format(auth)
    else:
        return 'Missing info: must add sender,receiver,message and subject'


@app.route('/get_all_messages', methods=['GET'])
def get_all_messages():
    if authentication.check_user_quary(request.args) or api.user:
        user = request.args.get('user') if not api.user else api.user
        return api.get_all_messeges(user)
    else:
        return 'User Not Found'


@app.route('/get_all_unread_messages', methods=['GET'])
def get_all_unread_messages():
    if authentication.check_user_quary(request.args) or api.user:
        user = request.args.get('user') if not api.user else api.user
        return api.get_all_unread_messages(user)
    else:
        return 'User Not Found'


@app.route('/read_message', methods=['GET'])
def read_message():
    if authentication.check_user_quary(request.args) or api.user:
        user = request.args.get('user') if not api.user else api.user
        return api.read_message(user)
    else:
        return 'User Not Found'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if not session.get('logged_in'):
        data = request.args
        LoginAuth(data.get('username'), data.get('password')).update_user_api_call(mongo, api)
        if api is not None:
            session['logged_in'] = True
            session['username'] = data.get('username')
            return 'Login Successfully '
        return 'Login Failed Username or Password are incorrect'
    else:
        return "You're logged in already!"


@app.route('/delete_message', methods=['GET'])
def delete_message():
    quary = request.args
    if authentication.check_user_quary(request.args) or api.user:
        user = request.args.get('user') if not api.user else api.user
    else:
        return 'User Not Found'
    To, From, tmsp, delete_as = authentication.check_and_parse_delete_quary(quary, user)
    return api.delete_message(To, From, tmsp, delete_as)


@app.route('/logout', methods=['GET'])
def logout():
    session['logged_in'] = False
    session['username'] = ''
    api.user = ''
    return "You're logged out"


if __name__ == '__main__':
    """in production  we use env var or flag for secret key"""
    # # api = Api(mongo)
    app.secret_key = 'simba'
    # app.run()



