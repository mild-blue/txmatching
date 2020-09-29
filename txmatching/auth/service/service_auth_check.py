from typing import Callable

from txmatching.auth.auth_check import require_role
from txmatching.auth.data_types import UserRole


def allow_service_role() -> Callable:
    """
    Allows user with role SERVICE to access the endpoint.
    """
    return require_role(UserRole.SERVICE)
