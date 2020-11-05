import functools
from typing import Callable

from txmatching.auth.data_types import TokenType, UserRole
from txmatching.auth.exceptions import WrongTokenUsedException
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
                raise WrongTokenUsedException(f'{TokenType.OTP} token required, but {token.type} received!')
            # this case should never happen, but we must be careful
            if token.role == UserRole.SERVICE:
                raise WrongTokenUsedException('OTP validation is only for user accounts.')

            return original_route(*args, **kwargs)

        return decorated_route

    return decorator
