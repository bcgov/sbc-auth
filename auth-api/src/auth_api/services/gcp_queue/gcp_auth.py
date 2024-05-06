# pylint: skip-file
# flake8: noqa
# This will get moved to an external library, which is linted by black (different than our rules)
"""Move this to external library."""
import functools
from http import HTTPStatus

import google.oauth2.id_token as id_token
from cachecontrol import CacheControl
from flask import abort, current_app, request
from google.auth.transport.requests import Request
from requests.sessions import Session


def verify_jwt(session):
    """Check token is valid with the correct audience and email claims for configured email address."""
    try:
        jwt_token = request.headers.get('Authorization', '').split()[1]
        claims = id_token.verify_oauth2_token(
            jwt_token,
            Request(session=session),
            audience=current_app.config.get('AUTH_SUB_AUDIENCE')
        )
        required_emails = current_app.config.get('VERIFY_PUBSUB_EMAILS')
        if claims.get('email_verified') and claims.get('email') in required_emails:
            return None
        else:
            return 'Email not verified or does not match', 401
    except Exception as e:
        return f'Invalid token: {e}', 400


def ensure_authorized_queue_user(f):
    """Ensures the user is authorized to use the queue."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Use CacheControl to avoid re-fetching certificates for every request.
        if verify_jwt(CacheControl(Session())):
            abort(HTTPStatus.UNAUTHORIZED)
        return f(*args, **kwargs)
    return decorated_function
