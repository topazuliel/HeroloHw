
def messege_parser(raw_messege):
    """remove the _id from mongodb"""
    raw_messege.pop('_id')
    raw_messege.pop('unread')
    return str(raw_messege)