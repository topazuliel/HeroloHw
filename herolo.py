import datetime

from flask import Flask, request
from flask_pymongo import PyMongo

import authentication
import messeges_utils
from db_connaction import DbConnection
from massage import Massage

db = DbConnection()

app = Flask(__name__)
app.config["MONGO_DBNAME"] = db.db_name
app.config["MONGO_URI"] = db.db_connection
mongo = PyMongo(app)
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello Herolo!'


@app.route('/write_message', methods=['GET', 'POST'])
def write_message():
    connect = None
    if request.method == 'POST':
        try:
            connect = mongo.db.Receiver
            quary = request.args
            auto = authentication.check_message_quary(quary)
            if auto == 'OK':
                massage = Massage(quary, str(datetime.datetime.now()))
                connect.insert(massage.json_message())
            elif auto != '':
                return 'Write message Failed {}'.format(auto)
            else:
                return 'Missing info: must add sender,receiver,message and subject'

            return 'Message send successfully'
        except:
            return 'Db Connection Failed'


@app.route('/get_all_messages', methods=['GET'])
def get_all_messeges():
    messges_send_str = ''
    messegs_received_str = ''
    parse_messages = list()
    if (authentication.check_user_quary(request.args)):
        user = request.args.get('user')
    else:
        return 'User Not Found'
    try:
        connect = mongo.db.Receiver
        messges_send = connect.find({'sender': user})
        messegs_received = connect.find({'receiver': user})
        if messegs_received.count() == 0 and messges_send.count() == 0:
            return "The user {} don't have any messages".format(user)
        if messges_send.count() != 0:
            for message in messges_send:
                parse_messages.append(messeges_utils.messege_parser(message))
            messges_send_str = ',\n'.join(parse_messages)

        parse_messages = []
        if messegs_received.count() != 0:
            for message in messegs_received:
                parse_messages.append(messeges_utils.messege_parser(message))
                messegs_received_str = ',\n'.join(parse_messages)


    except:
        return 'Db Connection Failed'

    return '{user} send messages:\n {send}\n\n{user}  received messages:\n {receive}'.format(user=user,
                                                                                             send=messges_send_str,
                                                                                             receive=messegs_received_str)


@app.route('/get_all_unread_messages', methods=['GET'])
def get_all_unread_messeges():
    messges_unread_str = ''
    parse_messages = list()

    if authentication.check_user_quary(request.args):
        user = request.args.get('user')
    else:
        return 'User Not Found'
    try:
        connect = mongo.db.Receiver
        messges_unread = connect.find({'receiver': user, 'unread': True})
        if messges_unread.count() != 0:
            for message in messges_unread:
                parse_messages.append(messeges_utils.messege_parser(message))
                messges_unread_str = ',\n'.join(parse_messages)
            return '{user} unread messages:\n {unread}'.format(user=user, unread=messges_unread_str)
        else:
            return "The user {} don't have any Unread messages".format(user)
    except:
        return 'Db Connection Failed'


@app.route('/read_message', methods=['GET'])
def read_message():
    if authentication.check_user_quary(request.args):
        user = request.args.get('user')
    else:
        return 'User Not Found'
    try:
        connect = mongo.db.Receiver
        messages_unread = connect.find_one({'receiver': user, 'unread': True})
        if len(messages_unread) is not None:
            connect.find_one_and_update({'_id': messages_unread['_id']}, {'$set': {'unread': False}})
            return messeges_utils.messege_parser(messages_unread)
        else:
            return "The user {} don't have any Unread messages".format(user)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    app.run()
