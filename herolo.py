import datetime
import messeges_utils
import authentication
from flask import Flask, request, jsonify
from passlib.hash import sha256_crypt
from flask_pymongo import PyMongo
from massage import Massage
from db_connaction import DbConnection

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


@app.route('/get_all_messages', methods=['GET', 'POST'])
def get_all_messeges():
    messges_send_str = ''
    messegs_received_str = ''
    parse_messages = list()
    user = request.args.get('user')
    try:
        connect = mongo.db.Receiver
        messges_send = connect.find({'sender': user})
        if (messges_send.count() != 0):
            for message in messges_send:
                parse_messages.append(messeges_utils.messege_parser(message))
            messges_send_str = ',\n'.join(parse_messages)
        messegs_received = connect.find({'receiver': user})
        parse_messages = []
        if (messegs_received.count() != 0):
            for message in messegs_received:
                parse_messages.append(messeges_utils.messege_parser(message))
                messegs_received_str = ',\n'.join(parse_messages)

    except:
        return 'Db Connection Failed'

    return '{user} send messages:\n {send}\n\n{user}  received messages:\n {receive}'.format(user=user,
                                                                                             send=messges_send_str,
                                                                                             receive=messegs_received_str)


@app.route('/get_all_unread_messages', methods=['GET', 'POST'])
def get_all_unread_messeges():
    messges_unread_str = ''
    parse_messages = list()
    user = request.args.get('user')
    try:
        connect = mongo.db.Receiver
        messges_unread = connect.find({'receiver': user, 'unread': True})
        if (messges_unread.count() != 0):
            for message in messges_unread:
                parse_messages.append(messeges_utils.messege_parser(message))
                messges_unread_str = ',\n'.join(parse_messages)

    except:
        return 'Db Connection Failed'

    return '{user} unread messages:\n {unread}'.format(user=user, unread=messges_unread_str, )


@app.route('/read_message', methods=['GET', 'POST'])
def read_message():
    if (request.method == 'POST'):
        user = request.args.get('user')
        try:
            connect = mongo.db.Receiver
            messge_unread = connect.find_one({'receiver': user, 'unread': True})
            connect.find_one_and_update({'_id': messges_unread['_id']}, {'$set': {'unread': False}})
            return messeges_utils.messege_parser(messge_unread)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    app.run()
