import functools
import logging
from typing import Callable

from flask import abort

from txmatching.auth.data_types import UserRole, TokenType
from txmatching.auth.request_context import get_request_token
from txmatching.auth.request_context import store_user_in_context

logger = logging.getLogger(__name__)


def require_role(*role_names: UserRole) -> Callable:
    """
    Checks logged user and correct role.
    """

    def decorator(original_route):
        @functools.wraps(original_route)
        def decorated_route(*args, **kwargs):
            token = get_request_token()

            if token.type != TokenType.ACCESS:
                abort(403, description='Authentication failed.')
            elif token.role not in role_names:
                abort(403, description='Access denied. You do not have privileges to view this page. If you believe'
                                       ' you are seeing this message by error, contact your administrator.')

            store_user_in_context(token.user_id, token.role)
            return original_route(*args, **kwargs)

        return decorated_route

    return decorator
