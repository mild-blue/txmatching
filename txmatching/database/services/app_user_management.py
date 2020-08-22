import logging
from typing import Union

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from txmatching.database.sql_alchemy_schema import AppUser

logger = logging.getLogger(__name__)


def get_all_app_users():
    return AppUser.query.all()


def get_app_user_by_email(email: str) -> Union[None, AppUser]:
    try:
        return AppUser.query.filter(AppUser.email == email).one()
    except MultipleResultsFound:
        logger.error("Multiple users with the same email found.")
        return None
    except NoResultFound:
        return None
