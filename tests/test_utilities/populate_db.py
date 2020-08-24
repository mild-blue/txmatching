from txmatching.database.services.app_user_management import persist_user
from txmatching.database.sql_alchemy_schema import AppUser
from txmatching.web.auth.crypto import encode_password

ADMIN_USER = ('admin@example.com', 'admin')


def add_users():
    email, password = ADMIN_USER
    persist_user(AppUser(
        email=email,
        pass_hash=encode_password(password),
        role='ADMIN')
    )
    assert AppUser.query.get(1) is not None
