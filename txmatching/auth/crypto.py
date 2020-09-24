import datetime
from typing import Union

import jwt

from txmatching.auth import bcrypt
from txmatching.auth.data_types import BearerToken, FailResponse, UserRole
from txmatching.configuration.app_configuration.application_configuration import get_application_configuration
from txmatching.database.sql_alchemy_schema import AppUserModel


def encode_password(password: str) -> str:
    """
    Encodes password to hash.
    """
    return bcrypt.generate_password_hash(password).decode()


def password_matches_hash(pwd_hash: str, password: str) -> bool:
    """
    >>> password_matches_hash(encode_password('hello'), 'hello')
    True
    >>> password_matches_hash(encode_password('hello'), 'not hello')
    False
    """
    return bcrypt.check_password_hash(pwd_hash, password)


def encode_auth_token(user: AppUserModel) -> bytearray:
    """
    Generates the Auth Token
    """
    app_conf = get_application_configuration()
    iat = datetime.datetime.utcnow()
    payload = {
        'user_id': user.id,
        'role': user.role,
        'iat': iat,
        'exp': _get_expiration_for_role(app_conf.jwt_expiration_days, iat, user.role)
    }
    return jwt.encode(
        payload,
        app_conf.jwt_secret,
        algorithm='HS256'
    )


def _get_expiration_for_role(
        default_expiration_days: int,
        iat: datetime.datetime,
        role: UserRole) -> datetime.datetime:
    if role == UserRole.SERVICE:
        # TODO https://trello.com/c/sRq4nFRv specify with the customer
        return iat + datetime.timedelta(minutes=2)

    return iat + datetime.timedelta(days=default_expiration_days)


def decode_auth_token(auth_token: str) -> Union[BearerToken, FailResponse]:
    """
    Validates the auth token, returns user mail on success, error message on failure.
    """
    try:
        app_conf = get_application_configuration()
        payload = jwt.decode(auth_token, app_conf.jwt_secret, algorithms=['HS256'])
        return BearerToken(int(payload['user_id']), UserRole(payload['role']))
    except jwt.ExpiredSignatureError:
        return FailResponse('Signature expired. Please log in again.')
    except jwt.InvalidTokenError:
        return FailResponse('Invalid token. Please log in again.')
