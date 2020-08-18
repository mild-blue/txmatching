import functools

from flask import abort
from flask import request

from kidney_exchange.web.auth.crypto import decode_auth_token


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
                    _, error = decode_auth_token(auth_token)
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
