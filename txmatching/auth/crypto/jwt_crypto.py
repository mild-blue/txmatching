import datetime

import jwt

from txmatching.auth.data_types import TokenType, UserRole, DecodedBearerToken
from txmatching.auth.exceptions import InvalidJWTException

JWT_SIGN_ALGORITHM = 'HS256'
"""
Algorithm used for signing JWT.

HS256 symmetric based on the HMAC.
"""


def parse_request_token(auth_header: str, jwt_secret: str) -> DecodedBearerToken:
    """
    Parses and verifies bearer token from the given string.
    Expects in format 'Bearer <token>'.
    """
    try:
        token_type, token = auth_header.split(' ')
        if token_type != 'Bearer':
            raise InvalidJWTException(f'Invalid token type! Expected "Bearer" but was {token_type}.')

        if not token:
            raise InvalidJWTException('Bearer token is empty.')

        return decode_auth_token(auth_token=token, jwt_secret=jwt_secret)
    # raised if split fails
    except (AttributeError, ValueError, KeyError) as missing_field:
        raise InvalidJWTException('Missing or invalid JWT.') from missing_field


def decode_auth_token(auth_token: str, jwt_secret: str) -> DecodedBearerToken:
    """
    Validates the auth token, returns DecodedBearerToken on success, raises exception on failure.
    """
    try:
        payload = jwt.decode(auth_token, jwt_secret, algorithms=[JWT_SIGN_ALGORITHM])
        return DecodedBearerToken(
            user_id=int(payload['user_id']),
            role=UserRole(payload['role']),
            type=TokenType(payload['type'])
        )
    except jwt.ExpiredSignatureError as expired_token:
        raise InvalidJWTException('Login expired. Please log in again.') from expired_token
    # InvalidTokenError - wrong token, formatting
    # ValueError - TokenType/UserRole could not be parsed, should not happen..
    except (jwt.InvalidTokenError, ValueError) as invalid_token:
        raise InvalidJWTException('Invalid token. Please log in again.') from invalid_token


def encode_auth_token(
        user_id: int,
        user_role: UserRole,
        token_type: TokenType,
        expiration: datetime.timedelta,
        jwt_secret: str
) -> str:
    """
    Generates the Auth Token from given parameters.
    """
    iat = datetime.datetime.utcnow()
    payload = {
        'user_id': user_id,
        'role': user_role,
        'type': token_type,
        'iat': iat,
        'exp': iat + expiration
    }
    return jwt.encode(
        payload,
        jwt_secret,
        algorithm=JWT_SIGN_ALGORITHM
    ).decode()
