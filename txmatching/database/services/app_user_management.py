import logging
from typing import Optional

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import AppUser

logger = logging.getLogger(__name__)


def get_all_app_users():
    return AppUser.query.all()


def get_app_user_by_email(email: str) -> Optional[AppUser]:
    try:
        return AppUser.query.filter(AppUser.email == email).one()
    except MultipleResultsFound:
        logger.error("Multiple users with the same email found.")
        return None
    except NoResultFound:
        return None


def persist_user(user: AppUser):
    # insert the user
    db.session.add(user)
    db.session.commit()
