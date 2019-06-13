class Massage():
    def __init__(self, quary, creation_date):
        self.__sender = quary.get('sender')
        self.__receiver = quary.get('receiver')
        self.__message = quary.get('message')
        self.__subject = quary.get('subject')
        self.__creation_date = creation_date

    @property
    def get_sender(self):
        return self.__sender

    @property
    def get_receiver(self):
        return self.__receiver

    @property
    def get_message(self):
        return self.__message

    @property
    def get_subject(self):
        return self.__subject

    @property
    def get_creation_date(self):
        return self.__creation_date

    def json_message(self):
        return dict(sender=self.__sender,receiver=self.__receiver,subject=self.__subject,message=self.__message,creation_date=self.__creation_date,unread=True)