# pylint: disable=broad-except
# as this is authentication, we need to catch everything

import logging
from typing import Union

from txmatching.auth.data_types import LoginSuccessResponse, FailResponse, UserRole
from txmatching.database.services.app_user_management import get_app_user_by_email, persist_user, \
    get_app_user_by_id, update_password_for_user
from txmatching.database.sql_alchemy_schema import AppUserModel
from txmatching.auth.crypto import password_matches_hash, encode_auth_token, decode_auth_token, encode_password

logger = logging.getLogger(__name__)
LoginResponse = Union[LoginSuccessResponse, FailResponse]


def obtain_login_token(email: str, password: str) -> LoginResponse:
    """
    Tries to verify user by given email and password,
    return tuple where first member is token, second is error message if any.
    """
    try:
        # fetch the user data
        user = get_app_user_by_email(email)
        if not user or not password_matches_hash(user.pass_hash, password):
            return FailResponse('Email password mismatch!')

        else:
            return LoginSuccessResponse(encode_auth_token(user).decode(), user.role)
    except Exception:
        logger.exception('Exception during user login.')
        return FailResponse('It was not possible to verify user.')


def refresh_token(auth_token: str) -> LoginResponse:
    """"
    If current token is valid, generates new one.
    """
    maybe_bearer_token = decode_auth_token(auth_token)
    if isinstance(maybe_bearer_token, FailResponse):
        return maybe_bearer_token
    # if the token is valid than this should always succeed
    # if not, we have inconsistent database or leaked JWT secret
    else:
        user = get_app_user_by_id(maybe_bearer_token.user_id)
        return LoginSuccessResponse(encode_auth_token(user).decode(), user.role)


def register_user(email: str, password: str, role: UserRole) -> LoginResponse:
    """
    Registers new user for given email, password and role.
    >>> register_user('', 'pwd', UserRole.ADMIN)
    (None, 'Incorrectly set values.')
    >>> register_user('email', '', UserRole.ADMIN)
    (None, 'Incorrectly set values.')
    >>> register_user('email', 'pwd', '')
    (None, 'Incorrectly set values.')
    """
    if not email or not password or not role:
        return FailResponse('Incorrectly set values.')

    user = get_app_user_by_email(email)
    if user:
        return FailResponse('The e-mail address is already in use.')
    try:
        user = AppUserModel(
            email=email,
            pass_hash=encode_password(password),
            role=role
        )

        persist_user(user)
    except Exception:
        logger.exception('Exception during saving user to database.')
        return FailResponse('It was not possible to register user!')

    auth_token = encode_auth_token(user).decode()
    return LoginSuccessResponse(auth_token, user.role)


def change_user_password(user_id: int, new_password: str):
    """
    Updates password for the user.
    """
    pwd_hash = encode_password(new_password)
    update_password_for_user(user_id=user_id, new_password_hash=pwd_hash)
