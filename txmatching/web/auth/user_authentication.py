# pylint: disable=broad-except
# as this is authentication, we need to catch everything

import logging
from typing import Optional, Tuple

from txmatching.database.services.app_user_management import get_app_user_by_email, persist_user, \
    get_app_user_by_id, update_password_for_user
from txmatching.database.sql_alchemy_schema import AppUser
from txmatching.web.auth.crypto import password_matches_hash, encode_auth_token, decode_auth_token, encode_password

logger = logging.getLogger(__name__)


def obtain_login_token(email: str, password: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Tries to verify user by given email and password,
    return tuple where first member is token, second is error message if any.
    """
    try:
        # fetch the user data
        user = get_app_user_by_email(email)
        error = None
        if not user or not password_matches_hash(user.pass_hash, password):
            error = None, 'Email password mismatch!'

        return error if error else (encode_auth_token(user).decode(), None)
    except Exception:
        logger.exception('Exception during user login.')
        return None, 'It was not possible to verify user.'


def refresh_token(auth_token: str) -> Tuple[Optional[str], Optional[str]]:
    """"
    If current token is valid, generates new one.
    """
    token, error = decode_auth_token(auth_token)
    if error:
        return None, error
    # if the token is valid than this should always succeed
    # if not, we have inconsistent database or leaked JWT secret
    user = get_app_user_by_id(token.user_id)
    return encode_auth_token(user).decode(), None


def register_user(email: str, password: str, role: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Registers new user for given email, password and role.
    >>> register_user('', 'pwd', 'role')
    (None, 'Incorrectly set values.')
    >>> register_user('email', '', 'role')
    (None, 'Incorrectly set values.')
    >>> register_user('email', 'pwd', '')
    (None, 'Incorrectly set values.')
    """
    if not email or not password or not role:
        return None, 'Incorrectly set values.'

    user = get_app_user_by_email(email)
    if user:
        return None, 'The e-mail address is already in use.'
    try:
        user = AppUser(
            email=email,
            pass_hash=encode_password(password),
            role=role
        )

        persist_user(user)
    except Exception:
        logger.exception('Exception during saving user to database.')
        return None, 'It was not possible to register user!'

    auth_token = encode_auth_token(user).decode()
    return auth_token, None


def change_user_password(user_id: int, new_password: str):
    """
    Updates password for the user.
    """
    pwd_hash = encode_password(new_password)
    update_password_for_user(user_id=user_id, new_password_hash=pwd_hash)
