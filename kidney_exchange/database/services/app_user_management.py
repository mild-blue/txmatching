import logging
from typing import Optional

from kidney_exchange.database.db import db
from kidney_exchange.database.sql_alchemy_schema import AppUser

logger = logging.getLogger(__name__)


def get_all_app_users():
    return AppUser.query.all()


def get_app_user_by_email(email: str) -> Optional[AppUser]:
    return AppUser.query.filter(AppUser.email == email).first()


def persist_user(user: AppUser):
    # insert the user
    db.session.add(user)
    db.session.commit()
