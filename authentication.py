def check_message_quary(quary):
    try:
        if quary.get('sender') == '' or quary.get('sender') is None:
            return "Please add sender"
        if quary.get('receiver') == '' or quary.get('receiver') is None:
            return "Please add receiver"
        if quary.get('message') is None:
            return "Please add message"
        if quary.get('subject') == '' or quary.get('subject') is None:
            return "Please add subject"

    except:
        return ''

    return 'OK'
