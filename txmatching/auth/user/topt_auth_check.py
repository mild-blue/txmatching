import functools
from typing import Callable

from flask_restx import abort

from txmatching.auth.data_types import TokenType, UserRole
from txmatching.auth.request_context import get_request_token


def allow_otp_request() -> Callable:
    """
    Allows request with OTP token type.
    """

    def decorator(original_route):
        @functools.wraps(original_route)
        def decorated_route(*args, **kwargs):
            token = get_request_token()

            if token.type != TokenType.OTP:
                abort(403, error='Wrong token used.',
                      description=f'{TokenType.OTP} token required, but {token.type} received!')
            # this case should never happen, but we must be careful
            elif token.role == UserRole.SERVICE:
                abort(403, error='Wrong token used.',
                      description='OTP validation is only for user accounts.')

            return original_route(*args, **kwargs)

        return decorated_route

    return decorator
