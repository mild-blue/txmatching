from typing import Callable

from txmatching.auth.auth_check import require_role
from txmatching.auth.data_types import UserRole


def require_user_login() -> Callable:
    """
    Requires login from user (not service)
    """
    return require_role(UserRole.ADMIN, UserRole.VIEWER, UserRole.EDITOR)
