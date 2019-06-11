db_string = "mongodb://herolo:herolo1!@ds235417.mlab.com:35417/herolo"
class DbConnection():
    def __init__(self,db_name="herolo",db_connection=db_string):
        self.db_name = db_name
        self.db_connection = db_connection