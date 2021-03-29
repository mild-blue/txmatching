from typing import Callable

from txmatching.auth.auth_check import require_role
from txmatching.auth.data_types import UserRole


def require_user_login() -> Callable:
    """
    Requires login from user (not service).
    """
    return require_role(UserRole.ADMIN, UserRole.VIEWER, UserRole.EDITOR)


def require_user_edit_config_access() -> Callable:
    """
    Requires user with edit configuration rights - ADMIN or EDITOR.
    """
    return require_role(UserRole.ADMIN, UserRole.EDITOR)


def require_user_edit_patients_access() -> Callable:
    """
    Requires user with edit patients rights - ADMIN, VIEWER or EDITOR.
    """
    return require_role(UserRole.ADMIN, UserRole.VIEWER, UserRole.EDITOR)
