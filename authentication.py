from api_calls import CollectionTags


def check_message_quary(quary,user):
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


def check_user_quary(quary):
    if quary.get('user') == '' or quary.get('user') is None:
        return False
    return True


def check_and_parse_delete_quary(quary, user=None):
    user_is_used = False
    To = None
    From = None
    Tmsp = None

    if quary.get('tmsp'):
        Tmsp = quary.get('tmsp')
    if (quary.get('from') == '' or quary.get('from') is None):
        if user is not None and not user_is_used:
            user_is_used = True
            From = user
            Delete_as = CollectionTags.Send.name
        else:
            return 'Please add "from" args'
    else:
        From = quary.get('from')
    if (quary.get('to') == '' or quary.get('to') is None):
        if user is not None and not user_is_used:
            user_is_used = True
            To = user
            Delete_as = CollectionTags.Receiver.name
        else:
            return 'Please add "to" args'
    else:
        To = quary.get('to')

    if user == To:
        Delete_as = CollectionTags.Receiver.name
    else:
        Delete_as = CollectionTags.Send.name

    return To,From,Tmsp,Delete_as