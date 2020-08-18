import datetime
from typing import Tuple, Optional

import jwt

from kidney_exchange.database.sql_alchemy_schema import AppUser
from kidney_exchange.web.app_configuration.application_configuration import get_application_configuration
from kidney_exchange.web.auth.bcrypt import bcrypt


def encode_password(password: str) -> str:
    return bcrypt.generate_password_hash(password).decode()


def compare_passwords(pwd_hash: str, password: str) -> bool:
    """
    >>> compare_passwords(encode_password('hello'), 'hello')
    True
    >>> compare_passwords(encode_password('hello'), 'not hello')
    False
    """
    return bcrypt.check_password_hash(pwd_hash, password)


def encode_auth_token(user: AppUser) -> bytearray:
    """
    Generates the Auth Token
    """
    app_conf = get_application_configuration()
    payload = {
        'user_email': user.email,
        'role': user.role,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=app_conf.jwt_expiration_days)
    }
    return jwt.encode(
        payload,
        app_conf.jwt_secret,
        algorithm='HS256'
    )


def decode_auth_token(auth_token: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Validates the auth token, returns user mail on success, error message on failure.
    """
    try:
        app_conf = get_application_configuration()
        payload = jwt.decode(auth_token, app_conf.jwt_secret)
        return payload['user_email'], None
    except jwt.ExpiredSignatureError:
        return None, 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return None, 'Invalid token. Please log in again.'
