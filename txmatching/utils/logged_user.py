from typing import Optional

from flask import g

from txmatching.database.services.app_user_management import get_app_user_by_id
from txmatching.database.sql_alchemy_schema import AppUserModel


def get_current_user_id() -> int:
    """
    Retrieves user id from the request context.

    Can trow AttributeError if not executed inside the Flask context.
    """
    return g.user_id


def get_current_user() -> Optional[AppUserModel]:
    """
    Retrieves user from DB based on request context user_id.

    Can trow AttributeError if not executed inside the Flask context.
    """
    user_model = get_app_user_by_id(g.user_id)
    return user_model
