from passlib.hash import sha256_crypt

from api_calls import CollectionTags


class LoginAuth(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def check_password_and_username(self, mongo):
        user = mongo.db.Users.find_one({CollectionTags.Username.value: self.username})
        if user is not None and sha256_crypt.verify(self.password, user.get(CollectionTags.Password.value)):
            return True
        return False

    def update_user_api_call(self, mongo, api):
        if self.check_password_and_username(mongo):
            api.user = self.username
            return True
        return False
