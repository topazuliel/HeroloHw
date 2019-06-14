"""it's only for MongoDB """

db_string = "mongodb://herolo:herolo1!@ds235417.mlab.com:35417/herolo"


class DbConfig():
    def __init__(self, db_name="herolo", db_connection=db_string):
        self.db_name = db_name
        self.db_connection = db_connection

    def connect_to_collection(self, db, name):
        return db.db[name]

    def get_connection(self, db, collection_name):
        return self.connect_to_collection(db,collection_name)
