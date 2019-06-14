from api_calls import CollectionTags


def check_message_query(quary, user):
    try:
        if quary.get('sender') == '' or quary.get('sender') is None:
            if user is None:
                return "Please add sender"
        if quary.get('receiver') == '' or quary.get('receiver') is None:
            return "Please add receiver"
        if quary.get('message') == '' or quary.get('message') is None:
            return "Please add message"
        if quary.get('subject') == '' or quary.get('subject') is None:
            return "Please add subject"

    except:
        return ''

    return 'OK'


def check_user_query(quary):
    if quary.get('user') == '' or quary.get('user') is None:
        return False
    return True


def check_and_parse_delete_query(query, user=None):
    user_is_used = False
    time_stamp = None
    error = None

    if query.get('tmsp'):
        time_stamp = query.get('tmsp')
    if (query.get('from') == '' or query.get('from') is None):
        if user is not None and not user_is_used:
            user_is_used = True
            send_from = user
        else:
            error = 'Please add "from" args'
            send_from = None
    else:
        send_from = query.get('from')
    if (query.get('to') == '' or query.get('to') is None):
        if user is not None and not user_is_used:
            user_is_used = True
            send_to = user
        else:
            error= 'Please add "to" args'
            send_to = None
    else:
        send_to = query.get('to')

    if user == send_to:
        delete_as = CollectionTags.Receiver.name
    else:
        delete_as = CollectionTags.Send.name

    return send_to, send_from, time_stamp, delete_as,error
