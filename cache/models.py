from couchdb.schema import *
from couchdb.schema import View

class CacheRow(Document):
    value    = TextField()
    expires  = DateTimeField()

    get_keys = View('get_keys', 
                    '''function(doc) {
                         emit(doc._id, doc);
                       }''',
                    name='all')
