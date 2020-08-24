import datetime
from dataclasses import dataclass
from typing import Tuple, Optional

import jwt

from txmatching.database.sql_alchemy_schema import AppUser
from txmatching.web.app_configuration.application_configuration import get_application_configuration
from txmatching.web.auth import bcrypt


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


def encode_auth_token(user: AppUser) -> bytearray:
    """
    Generates the Auth Token
    """
    app_conf = get_application_configuration()
    payload = {
        'user_id': user.id,
        'role': user.role,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=app_conf.jwt_expiration_days)
    }
    return jwt.encode(
        payload,
        app_conf.jwt_secret,
        algorithm='HS256'
    )


@dataclass(frozen=True)
class BearerToken:
    user_id: int
    role: str


def decode_auth_token(auth_token: str) -> Tuple[Optional[BearerToken], Optional[str]]:
    """
    Validates the auth token, returns user mail on success, error message on failure.
    """
    try:
        app_conf = get_application_configuration()
        payload = jwt.decode(auth_token, app_conf.jwt_secret)
        return BearerToken(int(payload['user_id']), payload['role']), None
    except jwt.ExpiredSignatureError:
        return None, 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return None, 'Invalid token. Please log in again.'
