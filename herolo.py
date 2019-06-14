from flask import Flask, request, session, jsonify
from flask_pymongo import PyMongo

import authentication
from api_calls import Api,CollectionTags
from db_config import DbConfig
from login_auth import LoginAuth

db = DbConfig()
app = Flask(__name__)
app.config["MONGO_DBNAME"] = db.db_name
app.config["MONGO_URI"] = db.db_connection
app.config['SECRET_KEY'] = "just for test"
mongo = PyMongo(app)
api = Api(mongo)


@app.before_first_request
def update_user():
    api.user = session.get(CollectionTags.Username.value)


@app.route('/')
def start():
    return ''


@app.route('/message/write', methods=['POST'])
def write_message():
    query = request.args
    auth = authentication.check_message_query(query, api.user)
    if auth == CollectionTags.Ok.value:
        api.write_message(query, api.user)
        return jsonify(dict(success=True, massage='Message send successfully'))
    if auth != '':
        return jsonify(dict(success=False, massage='Write message Failed {}'.format(auth)))
    else:
        return jsonify(dict(success=False, massage='Missing info: must add sender,receiver,message and subject'))


@app.route('/message/all', methods=['GET'])
def get_all_messages():
    if authentication.check_user_query(request.args) or api.user:
        user = request.args.get(CollectionTags.User.value) if not api.user else api.user
        return api.get_all_messeges(user)
    else:
        return jsonify(dict(success=False, massage='User Not Found'))


@app.route('/message/unread', methods=['GET'])
def get_all_unread_messages():
    if authentication.check_user_query(request.args) or api.user:
        user = request.args.get(CollectionTags.User.value) if not api.user else api.user
        return api.get_all_unread_messages(user)
    else:
        return jsonify(dict(success=False, massage='User Not Found'))


@app.route('/message/read', methods=['GET'])
def read_message():
    if authentication.check_user_query(request.args) or api.user:
        user = request.args.get(CollectionTags.User.value) if not api.user else api.user
        send_from = request.args.get(CollectionTags.From.value)
        return api.read_message(user,sender=send_from)
    else:
        return jsonify(dict(success=False, massage='User Not Found'))



@app.route('/message/delete', methods=['DELETE'])
def delete_message():
    quary = request.args
    if authentication.check_user_query(request.args) or api.user:
        user = request.args.get(CollectionTags.User.value) if not api.user else api.user
    else:
        return jsonify(dict(success=False,massage='User Not Found'))
    send_to, send_from, time_stamp, delete_as,error = authentication.check_and_parse_delete_query(quary, user)
    if error is not None:
        return jsonify(dict(success=False, massage=error))
    return api.delete_message(send_to, send_from, time_stamp, delete_as)

@app.route('/login', methods=['POST'])
def login():
    """POST http://127.0.0.1:5000/login?username=<username>&password=<password>"""
    if not session.get(CollectionTags.Login.value):
        data = request.args
        valid = LoginAuth(data.get(CollectionTags.Username.value), data.get(CollectionTags.Password.value)).update_user_api_call(mongo, api)
        if valid:
            session[CollectionTags.Login.value] = True
            session[CollectionTags.Username.value] = data.get(CollectionTags.Username.value)
            return jsonify(dict(success=True,massage='You Logged in'))
        return jsonify(dict(success=False,massage='Login Failed Username or Password are incorrect'))
    else:
        return jsonify(dict(success=False,massage="You're logged in already!"))


@app.route('/logout', methods=['GET'])
def logout():
    """ update the login flag,username cookie and user
    http://127.0.0.1:5000/logout"""
    session[CollectionTags.Login.value] = False
    session[CollectionTags.Username.value] = ''
    api.user = ''
    return jsonify(dict(success=True,massage="You're logged out"))


if __name__ == '__main__':
    """in production  we use env var or flag for secret key"""
    app.run()
