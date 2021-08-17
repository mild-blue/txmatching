import logging
from datetime import timedelta
from typing import List

from flask import current_app
from itsdangerous import BadSignature
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from txmatching.auth.crypto.password_crypto import password_matches_hash
from txmatching.auth.data_types import TokenType, UserRole
from txmatching.auth.exceptions import (CredentialsMismatchException,
                                        InvalidEmailException,
                                        InvalidTokenException,
                                        require_auth_condition)
from txmatching.auth.request_context import get_request_token, get_user_role
from txmatching.auth.service.service_auth_management import register_service
from txmatching.auth.user.user_auth_management import (change_user_password,
                                                       register_user)
from txmatching.database.services.app_user_management import (
    get_app_user_by_email, get_app_user_by_id, update_reset_token_for_user)
from txmatching.utils.country_enum import Country

logger = logging.getLogger(__name__)


def change_password(current_password: str, new_password: str):
    """
    Changes password for the current user.
    """
    request_token = get_request_token()
    require_auth_condition(request_token.role != UserRole.SERVICE,
                           f'{request_token.role} is not allowed to change the password!')
    require_auth_condition(request_token.type != TokenType.OTP,
                           f'{request_token.type} is not enough to change the password!')

    _change_password(request_token.user_id, current_password, new_password)


def _change_password(user_id: int, current_password: str, new_password: str):
    user = get_app_user_by_id(user_id)
    if not password_matches_hash(user.pass_hash, current_password):
        raise CredentialsMismatchException()

    change_user_password(user_id, new_password)


def get_reset_token(email_to_reset_password: str):
    user_to_reset_password = get_app_user_by_email(email_to_reset_password)
    if user_to_reset_password is None:
        raise InvalidEmailException(f'User with email {email_to_reset_password} not found.')

    expires_sec = timedelta(weeks=1).total_seconds()
    s = Serializer(current_app.secret_key, expires_sec)
    reset_token = s.dumps({'user_id': user_to_reset_password.id}).decode('utf-8')

    update_reset_token_for_user(user_to_reset_password.id, reset_token)
    return reset_token


def reset_password(reset_token: str, new_password: str):
    user = get_app_user_by_id(_verify_reset_token(reset_token))
    if user.reset_token != reset_token:
        raise InvalidTokenException('Reset password token is invalid.')

    change_user_password(user.id, new_password)
    update_reset_token_for_user(user.id, None)


def _verify_reset_token(token: str):
    try:
        s = Serializer(current_app.secret_key)
        user_id = s.loads(token)['user_id']
    except BadSignature as bad_sign:
        raise InvalidTokenException('Reset password token is invalid.') from bad_sign
    return user_id


def register(email: str, password: str, role: UserRole, second_factor: str, allowed_countries: List[Country]):
    """
    Registers new user entity.
    """
    if role == UserRole.SERVICE:
        register_service(email=email, password=password, allowed_countries=allowed_countries,
                         whitelisted_ip=second_factor)
    else:
        register_user(email=email, password=password, allowed_countries=allowed_countries, role=role,
                      phone_number=second_factor)
