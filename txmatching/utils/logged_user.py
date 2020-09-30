from typing import Optional

from flask import g

from txmatching.data_transfer_objects.app_user.app_user import AppUser
from txmatching.database.services import txm_event_service
from txmatching.database.services.app_user_management import get_app_user_by_id


def get_current_user_id() -> int:
    """
    Retrieves user id from the request context.

    Can trow AttributeError if not executed inside the Flask context.
    """
    return g.user_id


def get_current_user() -> Optional[AppUser]:
    """
    Retrieves user from DB based on request context user_id.

    Can trow AttributeError if not executed inside the Flask context.
    """
    user_model = get_app_user_by_id(g.user_id)
    # TODO change in https://trello.com/c/xRmQhnqM
    if user_model.default_txm_event_id is None:
        user_model.default_txm_event_id = txm_event_service.get_newest_txm_event_db_id()
    return AppUser(user_model.email, user_model.role, user_model.default_txm_event_id)
