import logging
from typing import Optional

from txmatching.database.db import db
from txmatching.database.sql_alchemy_schema import AppUserModel

logger = logging.getLogger(__name__)


def get_all_app_users():
    return AppUserModel.query.all()


def get_app_user_by_email(email: str) -> Optional[AppUserModel]:
    return AppUserModel.query.filter(AppUserModel.email == email.lower()).first()


def get_app_user_by_id(user_id: int) -> Optional[AppUserModel]:
    return AppUserModel.query.get(user_id)


def persist_user(user: AppUserModel):
    # insert the user
    db.session.add(user)
    db.session.commit()
    return user


def update_password_for_user(user_id: int, new_password_hash: str):
    get_app_user_by_id(user_id).pass_hash = new_password_hash
    db.session.commit()
