import logging
from typing import Optional, Tuple

from kidney_exchange.database.services.app_user_management import get_app_user_by_email, persist_user
from kidney_exchange.database.sql_alchemy_schema import AppUser
from kidney_exchange.web.auth.crypto import compare_passwords, encode_auth_token, decode_auth_token, encode_password

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
        if not user:
            error = None, 'User does not exist!'
        elif not compare_passwords(user.pass_hash, password):
            # TODO - this is in a fact security vulnerability, we leaking information that user exist
            # TODO - to discuss with a team, how do we want to proceed
            error = None, 'Passwords do not match!'

        return error if error else (encode_auth_token(user).decode(), None)
    except Exception as e:
        logger.error(e)
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
    user = get_app_user_by_email(token.user_email)
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

    user = AppUser(
        email=email,
        pass_hash=encode_password(password),
        role=role
    )

    persist_user(user)
    auth_token = encode_auth_token(user).decode()
    return auth_token, None
