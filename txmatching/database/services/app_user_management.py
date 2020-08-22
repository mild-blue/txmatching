import logging
from typing import Optional

from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import AppUser

logger = logging.getLogger(__name__)


def get_all_app_users():
    return AppUser.query.all()


def get_app_user_by_email(email: str) -> Optional[AppUser]:
    return AppUser.query.filter(AppUser.email == email).first()


def get_app_user_by_id(user_id: int) -> Optional[AppUser]:
    return AppUser.query.get(user_id)


def persist_user(user: AppUser):
    # insert the user
    db.session.add(user)
    db.session.commit()


def update_password_for_user(email: str, new_password_hash: str):
    get_app_user_by_email(email).pass_hash = new_password_hash
    db.session.commit()
