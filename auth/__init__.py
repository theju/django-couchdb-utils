from django.conf import settings
import datetime

SESSION_KEY = '_auth_user_id'
BACKEND_SESSION_KEY = '_auth_user_backend'

def login(request, user):
    from auth.models import User
    if user is None:
        user = request.user
    # TODO: It would be nice to support different login methods, like signed cookies.
    backend = getattr(user, 'backend', getattr(settings, 'AUTHENTICATION_BACKENDS'))

    user = User.get_user(user.username)
    user.last_login = datetime.datetime.now()
    user.save()

    if SESSION_KEY in request.session:
        if request.session[SESSION_KEY] != user.username:
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
