from couchdb.schema import *

class Session(Document):
    session_data = TextField()
    expire_date  = TextField()
