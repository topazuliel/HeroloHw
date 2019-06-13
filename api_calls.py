import datetime
from enum import Enum

import messeges_utils
from db_connaction import DbConfig
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

    def write_message(self, data):
        """Write a message to DB"""
        try:
            send_collection = self.get_collection(CollectionTags.Send.name)
            received_collection = self.get_collection(CollectionTags.Receiver.name)
            massage = Massage(data, str(datetime.datetime.now()))
            send_collection.insert(massage.json_message())
            received_collection.insert(massage.json_message())
        except Exception as e:
            print(e)
            return 'Db Connection Failed'

    def get_all_messeges(self, user):
        """Get all received and send messages of specific user """
        parse_messages = list()
        messages_send_str = ''
        messags_received_str = ''
        try:
            messages_send = self.get_collection(CollectionTags.Send.name).find({'sender': user})
            messags_received = self.get_collection(CollectionTags.Receiver.name).find({'receiver': user})
            if messags_received.count() == 0 and messages_send.count() == 0:
                return "The user {} don't have any messages".format(user)
            if messages_send.count() != 0:
                for message in messages_send:
                    parse_messages.append(messeges_utils.messege_parser(message))
                    messages_send_str = ',\n'.join(parse_messages)

            parse_messages = []
            if messags_received.count() != 0:
                for message in messags_received:
                    parse_messages.append(messeges_utils.messege_parser(message))
                    messags_received_str = ',\n'.join(parse_messages)


        except:
            return 'Db Connection Failed'

        return '{user} send messages:\n {send}\n\n{user}  received messages:\n {receive}'.format(user=user,
                                                                                                 send=messages_send_str,
                                                                                                 receive=messags_received_str)

    def get_all_unread_messages(self, user):
        """Get all received unread messages of specific user"""
        messages_unread_str = ''
        parse_messages = list()
        try:
            collection = self.get_collection(CollectionTags.Receiver.name)
            messges_unread = collection.find({'receiver': user, 'unread': True})
            if messges_unread.count() != 0:
                for message in messges_unread:
                    parse_messages.append(messeges_utils.messege_parser(message))
                    messages_unread_str = ',\n'.join(parse_messages)
                return '{user} unread messages:\n {unread}'.format(user=user, unread=messages_unread_str)
            else:
                return "The user {} don't have any Unread messages".format(user)
        except:
            return 'Db Connection Failed'

    def read_message(self, user):
        """Read a random message of specific user and update the message to read"""
        try:
            collection = self.get_collection(CollectionTags.Receiver.name)
            messages_unread = collection.find_one({'receiver': user, 'unread': True})
            if messages_unread is not None:
                collection.find_one_and_update({'_id': messages_unread['_id']}, {'$set': {'unread': False}})
                return messeges_utils.messege_parser(messages_unread)
            else:
                return "The user {} don't have any Unread messages".format(user)

        except Exception as e:
            print(e)

    def delete_message(self, To, From, tmsp,delete_as):
        collection = self.get_collection(delete_as)
        if tmsp is not None:
            collection.delete_one({'creation_date': tmsp})
            return "Message as been deleted"
        elif delete_as == CollectionTags.Send.name:
            collection.delete_one({'sender':From,'receiver': To})
            return "Message as been deleted"
        else:
            collection.delete_one({'sender': From, 'receiver': To, 'unread': False})
            return "Message as been deleted"


    def get_collection(self,collection_name):
        return self.db.connect_to_collection(self.mongo, collection_name)
