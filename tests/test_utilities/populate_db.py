from txmatching.database.services.app_user_management import persist_user
from txmatching.database.sql_alchemy_schema import AppUser
from txmatching.web.auth.crypto import encode_password

ADMIN_USER = {
    'id': 1,
    'email': 'admin@example.com',
    'password': 'admin'
}


def add_users():
    app_user = AppUser(
        email=ADMIN_USER['email'],
        pass_hash=encode_password(ADMIN_USER['password']),
        role='ADMIN')
    persist_user(app_user)
    ADMIN_USER['id'] = app_user.id
    assert AppUser.query.get(1) is not None
