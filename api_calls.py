import datetime
from enum import Enum

from flask import jsonify

import messeges_utils
from db_config import DbConfig
from massage import Massage


class CollectionTags(Enum):
    Send = 'send'
    Receiver = 'received'


class Api():
    def __init__(self, mongo, user=None, db_config=None):
        self.user = user
        self.mongo = mongo
        if db_config is None:
            self.db = DbConfig()
        else:
            self.db = db_config

    def write_message(self, data, user):
        """Write a message to DB"""
        try:
            send_collection = self.get_collection(CollectionTags.Send.name)
            received_collection = self.get_collection(CollectionTags.Receiver.name)
            massage = Massage(data, str(datetime.datetime.now()),user)
            send_collection.insert(massage.json_message())
            received_collection.insert(massage.json_message())
        except Exception as e:
            print(e)
            return jsonify(dict(success=False,massage='Db Connection Failed'))

    def get_all_messeges(self, user):
        """Get all received and send messages of specific user """
        send_parse_messages = list()
        receive_parse_messages = list()
        try:
            messages_send = self.get_collection(CollectionTags.Send.name).find({'sender': user})
            messags_received = self.get_collection(CollectionTags.Receiver.name).find({'receiver': user})
            if messags_received.count() == 0 and messages_send.count() == 0:
                return "The user {} don't have any messages".format(user)
            if messages_send.count() != 0:
                for message in messages_send:
                    send_parse_messages.append(messeges_utils.messege_parser(message))

            if messags_received.count() != 0:
                for message in messags_received:
                    receive_parse_messages.append(messeges_utils.messege_parser(message))


        except:
            return jsonify(dict(success=False,massage='Db Connection Failed'))

        return jsonify(dict(success=True, user=user,send=send_parse_messages,received=receive_parse_messages))

    def get_all_unread_messages(self, user):
        """Get all received unread messages of specific user"""
        parse_messages = list()
        try:
            collection = self.get_collection(CollectionTags.Receiver.name)
            messges_unread = collection.find({'receiver': user, 'unread': True})
            if messges_unread.count() != 0:
                for message in messges_unread:
                    parse_messages.append(messeges_utils.messege_parser(message))
                return jsonify(dict(success=True, user=user,massages=parse_messages))
            else:
                return  jsonify(dict(success=True, user=user,massages=''))
        except:
            return jsonify(dict(success=False,massage='Db Connection Failed'))

    def read_message(self, user):
        """Read a random message of specific user and update the message to read"""
        try:
            collection = self.get_collection(CollectionTags.Receiver.name)
            messages_unread = collection.find_one({'receiver': user, 'unread': True})
            if messages_unread is not None:
                collection.find_one_and_update({'_id': messages_unread['_id']}, {'$set': {'unread': False}})
                return jsonify(dict(success=True, user=user,massages=messeges_utils.messege_parser(messages_unread)))
            else:
                return jsonify(dict(success=False,massage="The user {} don't have any Unread messages".format(user)))

        except Exception as e:
            print(e)

    def delete_message(self, send_to, send_from, time_stamp, delete_as):
        collection = self.get_collection(delete_as)
        if time_stamp is not None:
            collection.delete_one({'creation_date': time_stamp})
        elif delete_as == CollectionTags.Send.name:
            collection.delete_one({'sender': send_from, 'receiver': send_to})
        else:
            collection.delete_one({'sender': send_from, 'receiver': send_to, 'unread': False})
        return "Message as been deleted"

    def get_collection(self, collection_name):
        return self.db.connect_to_collection(self.mongo, collection_name)
