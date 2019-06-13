
def messege_parser(raw_messege):
    """remove the _id and Flag from mongodb"""
    raw_messege.pop('_id')
    raw_messege.pop('unread')
    raw_messege.pop('creation_date')
    return str(raw_messege)

def tmsp(message):
    return message.get('creation_date')