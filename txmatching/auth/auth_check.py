import functools
import logging
from typing import Callable

from txmatching.auth.data_types import TokenType, UserRole
from txmatching.auth.exceptions import (AuthenticationException,
                                        InvalidArgumentException,
                                        UnauthorizedException,
                                        WrongTokenUsedException)
from txmatching.auth.request_context import (get_request_token,
                                             store_user_in_context)
from txmatching.database.services.txm_event_service import \
    get_allowed_txm_event_ids_for_current_user

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
                raise WrongTokenUsedException(
                    f'Wrong token type used, expected TokenType.ACCESS, but was {token.type}.')
            if token.role not in role_names:
                raise AuthenticationException(
                    'Access denied. You do not have privileges to view this page. If you believe you are seeing this'
                    ' message by error, contact your administrator.'
                )

            store_user_in_context(token.user_id, token.role)
            return original_route(*args, **kwargs)

        return decorated_route

    return decorator


def require_valid_txm_event_id() -> Callable:
    """
    Checks that the user has permission to access route parameter txm_event_id
    """

    def decorator(original_route):
        @functools.wraps(original_route)
        def decorated_route(*args, **kwargs):
            txm_event_id = kwargs.get('txm_event_id', None)
            if txm_event_id is None:
                raise InvalidArgumentException(f'Argument txm_event_id is not specified.')

            if txm_event_id not in get_allowed_txm_event_ids_for_current_user():
                raise UnauthorizedException(f'TXM event {txm_event_id} is not allowed for this user.')

            return original_route(*args, **kwargs)

        return decorated_route

    return decorator
