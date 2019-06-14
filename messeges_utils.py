def messege_parser(raw_message):
    """remove the _id and Flag from message"""
    raw_message.pop('_id')
    raw_message.pop('unread')
    # raw_messege.pop('creation_date')
    return str(raw_message)


def tmsp(message):
    return message.get('creation_date')
