# pylint: disable=broad-except
# as this is authentication, we need to catch everything

import functools
import logging
from typing import Union

from flask import abort, g
from flask import request
from werkzeug.datastructures import EnvironHeaders

from txmatching.auth.crypto import decode_auth_token
from txmatching.auth.data_types import BearerToken, FailResponse, UserRole

logger = logging.getLogger(__name__)


def get_request_token() -> Union[BearerToken, FailResponse]:
    """
    Returns token of the currently logged in user.

    Token is present in the header Authorization: Bearer <real_token>
    """
    auth_header = request.headers.get('Authorization')
    try:
        auth_token = auth_header.split(' ')[1]
        return decode_auth_token(auth_token)
    except Exception:
        return FailResponse('Exception during token parsing.')


def _get_token(headers: EnvironHeaders) -> Union[BearerToken, FailResponse]:
    auth_header = headers.get('Authorization')
    if auth_header:
        try:
            auth_token = auth_header.split(" ")[1]
            return decode_auth_token(auth_token)
        except Exception:
            return FailResponse('Bearer token malformed.')
    else:
        return FailResponse('Access denied.')


def login_required():
    """
    Verifies, that user is logged in.
    """

    def decorator(original_route):
        @functools.wraps(original_route)
        def decorated_route(*args, **kwargs):
            maybe_token = _get_token(request.headers)

            if isinstance(maybe_token, FailResponse):
                abort(401, description='Authentication denied.')
            store_user_in_context(maybe_token.user_id)
            return original_route(*args, **kwargs)

        return decorated_route

    return decorator


def require_role(*role_names: UserRole):
    """
    Checks logged user and whether he/she has correct role.
    """

    def decorator(original_route):
        @functools.wraps(original_route)
        def decorated_route(*args, **kwargs):
            maybe_token = _get_token(request.headers)

            if isinstance(maybe_token, FailResponse):
                abort(401, description='Authentication denied.')

            if maybe_token.role not in role_names:
                abort(401, description='Authentication denied, role mismatch!')

            return original_route(*args, **kwargs)

        return decorated_route

    return decorator


def get_user_role():
    """
    Checks logged user and whether he/she has correct role.
    """

    def decorator(original_route):
        @functools.wraps(original_route)
        def decorated_route(*args, **kwargs):
            maybe_token = _get_token(request.headers)

            return original_route(user_role=maybe_token.role, *args, **kwargs)

        return decorated_route

    return decorator


def store_user_in_context(user_id: int):
    """
    Sets user id for the current request context.
    """
    g.user_id = user_id
