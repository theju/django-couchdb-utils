from django.conf import settings
import datetime, couchdb, urlparse
from couchdb.client import PreconditionFailed

SESSION_KEY = '_auth_user_id'
BACKEND_SESSION_KEY = '_auth_user_backend'
DEFAULT_COUCHDB_HOST = 'http://localhost:5984/'

def get_or_create(server_uri, db_name):
    server = couchdb.Server(server_uri)
    try:
        db = server.create(db_name)
    except PreconditionFailed, e:
        if not e.message[0] == 'file_exists':
            raise e
        # Database seems to exist. Let's just use it
        db = couchdb.Database(urlparse.urljoin(server_uri, db_name))
    return db

def login(request, user):
    from auth.models import User, DB_PREFIX
    if user is None:
        user = request.user
    # TODO: It would be nice to support different login methods, like signed cookies.
    backend = getattr(user, 'backend', getattr(settings, 'AUTHENTICATION_BACKENDS'))
    server_uri = getattr(settings, 'COUCHDB_HOST', DEFAULT_COUCHDB_HOST)
    auth_db = get_or_create(server_uri, "%sauth" %DB_PREFIX)
    user = User.load(auth_db, user.id)
    user.last_login = datetime.datetime.now()
    user.store(auth_db)

    if SESSION_KEY in request.session:
        if request.session[SESSION_KEY] != user.id:
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
    else:
        request.session.cycle_key()
    request.session[SESSION_KEY] = user.id
    request.session[BACKEND_SESSION_KEY] = backend
    if hasattr(request, 'user'):
        request.user = user
