import datetime
from enum import Enum

from flask import jsonify

import messeges_utils
from db_config import DbConfig
from message import Massage


class CollectionTags(Enum):
    Send = 'send'
    Receiver = 'received'
    User = 'user'
    From = 'from'
    Username = 'username'
    Password = 'password'
    Login = 'logged_in'
    To = 'to'
    Time_Stamp = 'tmsp'
    Ok = 'OK'


class Api():
    def __init__(self, mongo, user=None, db_config=None):
        self.user = user
        self.mongo = mongo
        if db_config is None:
            self.db = DbConfig()
        else:
            self.db = db_config

    def write_message(self, data, user):
        """Write a message to DB
        POST http://127.0.0.1:5000/message/write?sender=<username>&receiver=<username>&message=<message>&subject=<subject> if login
        don't need to pass sender """
        try:
            send_collection = self.db.get_connection(self.mongo, CollectionTags.Send.name)
            received_collection = self.db.get_connection(self.mongo, CollectionTags.Receiver.name)
            massage = Massage(data, str(datetime.datetime.now()), user)
            send_collection.insert(massage.json_message())
            received_collection.insert(massage.json_message())
        except Exception as e:
            return jsonify(dict(success=False, message=e))

    def get_all_messeges(self, user):
        """Get all received and send messages of specific user
        GET http://127.0.0.1:5000/message/all if login.
        GET http://127.0.0.1:5000//message/all?user=<username>"""
        send_parse_messages = list()
        receive_parse_messages = list()
        try:
            messages_send = self.db.get_connection(self.mongo, CollectionTags.Send.name).find({'sender': user})
            messags_received = self.db.get_connection(self.mongo, CollectionTags.Receiver.name).find({'receiver': user})
            if messags_received.count() == 0 and messages_send.count() == 0:
                return jsonify(
                    dict(success=True, user=user, mesages="The user don't have any messages"))
            if messages_send.count() != 0:
                for message in messages_send:
                    send_parse_messages.append(messeges_utils.messege_parser(message))

            if messags_received.count() != 0:
                for message in messags_received:
                    receive_parse_messages.append(messeges_utils.messege_parser(message))


        except Exception as e:
            return jsonify(dict(success=False, message=e))

        return jsonify(dict(success=True, user=user, send=send_parse_messages, received=receive_parse_messages))

    def get_all_unread_messages(self, user):
        """Get all received unread messages of specific user
        GET http://127.0.0.1:5000/message/unread if login.
        GET http://127.0.0.1:5000//message/unread?user=<username>"""
        parse_messages = list()
        try:
            collection = self.db.get_connection(self.mongo, CollectionTags.Receiver.name)
            messges_unread = collection.find({'receiver': user, 'unread': True})
            if messges_unread.count() != 0:
                for message in messges_unread:
                    parse_messages.append(messeges_utils.messege_parser(message))
                return jsonify(dict(success=True, user=user, message=parse_messages))
            else:
                return jsonify(dict(success=True, user=user, mesages="The user don't have any messages"))
        except Exception as e:
            return jsonify(dict(success=False, message=e))

    def read_message(self, user, sender=None):
        """Read a random message of specific user and update the message to read
        GET http://127.0.0.1:5000/message/read?from=<username> or GET http://127.0.0.1:5000/message/read if login.
        GET http://127.0.0.1:5000//message/read?user=<username>&from=<username>"""
        try:
            query = {'receiver': user, 'unread': True} if not sender else {'sender': sender, 'receiver': user,
                                                                           'unread': True}
            collection = self.db.get_connection(self.mongo, CollectionTags.Receiver.name)
            messages_unread = collection.find_one(query)
            if messages_unread is not None:
                collection.find_one_and_update({'_id': messages_unread['_id']}, {'$set': {'unread': False}})
                return jsonify(dict(success=True, user=user, messages=messeges_utils.messege_parser(messages_unread)))
            else:
                return jsonify(dict(success=False, message="The user {} don't have any Unread messages".format(user)))

        except Exception as e:
            jsonify(dict(success=False, message=e))

    def delete_message(self, send_to, send_from, time_stamp, delete_as):
        """DELETE http://127.0.0.1:5000/message/delete?from=<username>&to=<username>&tmsp=<time stamp> if login
        can pass only 'from' or 'to' depend if need to delete as owner or rec"""
        send_collection = self.db.get_connection(self.mongo, CollectionTags.Send.value)
        receive_collection = self.db.get_connection(self.mongo, CollectionTags.Receiver.value)
        query = {'sender': send_from, 'receiver': send_to}
        if time_stamp is not None:
            is_deleted = send_collection.delete_one({'creation_date': time_stamp})
            if not is_deleted.deleted_count:
                is_deleted = receive_collection.delete_one({'creation_date': time_stamp})
        elif delete_as == CollectionTags.Send.name:
            is_deleted = send_collection.delete_one(query)
        else:
            is_deleted = receive_collection.delete_one(query)
        if is_deleted.deleted_count:
            return jsonify(dict(success=True, messages="The Message has been deleted"))
        return jsonify(dict(success=False, messages="Message not found"))

