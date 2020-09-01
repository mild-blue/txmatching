# pylint: disable=broad-except
# as this is authentication, we need to catch everything

import functools
import logging
from typing import Optional

from flask import abort, g
from flask import request

from txmatching.web.auth.crypto import decode_auth_token, BearerToken

logger = logging.getLogger(__name__)


def get_request_token() -> Optional[BearerToken]:
    """
    Returns token of the currently logged in user.

    Token is present in the header Authorization: Bearer <real_token>
    """
    auth_header = request.headers.get('Authorization')
    token = None
    try:
        auth_token = auth_header.split(' ')[1]
        token, _ = decode_auth_token(auth_token)
    except Exception:
        logger.exception('Exception during token parsing.')
    return token


def login_required():
    """
    Verifies, that user is logged in.
    """

    def decorator(original_route):
        @functools.wraps(original_route)
        def decorated_route(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if auth_header:
                try:
                    auth_token = auth_header.split(" ")[1]
                    token, error = decode_auth_token(auth_token)
                    store_user_in_context(token.user_id)
                except Exception:
                    error = 'Bearer token malformed.'
            else:
                error = 'Access denied.'

            if error:
                abort(401, description='Authentication denied.')

            return original_route(*args, **kwargs)

        return decorated_route

    return decorator


def require_role(*role_names):
    """
    Checks logged user and whether he/she has correct role.
    """

    def decorator(original_route):
        @functools.wraps(original_route)
        def decorated_route(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            token, error = None, None
            if auth_header:
                try:
                    auth_token = auth_header.split(" ")[1]
                    token, error = decode_auth_token(auth_token)
                    store_user_in_context(token.user_id)
                except Exception:
                    error = 'Bearer token malformed.'
            else:
                error = 'Access denied.'

            if error or not token:
                abort(401, description='Authentication denied.')

            if token.role not in role_names:
                abort(401, description='Authentication denied, role mismatch!')

            return original_route(*args, **kwargs)

        return decorated_route

    return decorator


def store_user_in_context(user_id: int):
    """
    Sets user id for the current request context.
    """
    g.user_id = user_id
