import logging
from datetime import timedelta

from itsdangerous import BadSignature
from itsdangerous import URLSafeTimedSerializer as Serializer

from txmatching.auth.crypto.password_crypto import password_matches_hash
from txmatching.auth.data_types import TokenType, UserRole
from txmatching.auth.exceptions import (CredentialsMismatchException,
                                        InvalidEmailException,
                                        InvalidTokenException,
                                        require_auth_condition)
from txmatching.auth.request_context import get_request_token
from txmatching.auth.service.service_auth_management import register_service
from txmatching.auth.user.user_auth_management import (change_user_password,
                                                       register_user)
from txmatching.configuration.app_configuration.application_configuration import \
    get_application_configuration
from txmatching.data_transfer_objects.users.user_dto import \
    UserRegistrationDtoIn
from txmatching.database.services.app_user_management import (
    get_app_user_by_email, get_app_user_by_id, update_reset_token_for_user)
from txmatching.database.services.txm_event_service import (
    get_txm_event_db_id_by_name, set_allowed_txm_event_ids_for_user)

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


def get_user_id_for_email(email: str) -> int:
    user_to_reset_password = get_app_user_by_email(email)
    if user_to_reset_password is None:
        raise InvalidEmailException(f'User with email {email} not found.')
    return user_to_reset_password.id


def get_reset_token(user_id: int) -> str:
    token = _get_reset_token(get_application_configuration().jwt_secret, user_id)
    # store that there's an active password reset token for the user
    update_reset_token_for_user(user_id, token)

    return token


def _get_reset_token(secret_key: str, user_id: int) -> str:
    token = _create_serializer(secret_key).dumps({'user_id': user_id})
    return token


def reset_password(reset_token: str, new_password: str):
    user_id = verify_reset_token(reset_token)
    maybe_user = get_app_user_by_id(user_id)
    if maybe_user is None:
        raise InvalidEmailException(f'User with email {user_id} not found.')
    # check if there's an active reset token
    if maybe_user.reset_token != reset_token:
        raise InvalidTokenException('Reset password token is invalid.')
    # change password
    change_user_password(maybe_user.id, new_password)
    # and delete activity flag
    update_reset_token_for_user(maybe_user.id, None)


def verify_reset_token(token: str) -> int:
    return _verify_reset_token(get_application_configuration().jwt_secret, token)


def _verify_reset_token(secret_key: str, reset_token: str, expiration: timedelta = timedelta(weeks=1)) -> int:
    try:
        expiration_seconds = int(expiration.total_seconds())
        user_id = _create_serializer(secret_key).loads(reset_token, max_age=expiration_seconds)['user_id']
    except BadSignature as bad_sign:
        raise InvalidTokenException('Reset password token is invalid.') from bad_sign

    return user_id


def _create_serializer(secret_key: str) -> Serializer:
    return Serializer(secret_key, salt=b'mild-blue-txm')


def register(registration_dto: UserRegistrationDtoIn) -> str:
    """
    Registers new user entity.
    """
    txm_event_ids = [get_txm_event_db_id_by_name(name) for name in registration_dto.allowed_txm_events]
    if registration_dto.role == UserRole.SERVICE:
        user_model = register_service(email=registration_dto.email, password=registration_dto.password,
                                      allowed_countries=registration_dto.allowed_countries,
                                      whitelisted_ip=registration_dto.second_factor,
                                      require_second_factor=registration_dto.require_second_factor)
    else:
        user_model = register_user(email=registration_dto.email, password=registration_dto.password,
                                   allowed_countries=registration_dto.allowed_countries, role=registration_dto.role,
                                   phone_number=registration_dto.second_factor,
                                   require_second_factor=registration_dto.require_second_factor)

    set_allowed_txm_event_ids_for_user(user_model, txm_event_ids)
    return get_reset_token(user_model.id)
