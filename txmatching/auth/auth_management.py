from txmatching.auth.crypto.password_crypto import password_matches_hash
from txmatching.auth.data_types import UserRole, TokenType
from txmatching.auth.exceptions import require_auth_condition, CredentialsMismatchException
from txmatching.auth.request_context import get_request_token
from txmatching.auth.service.service_auth_management import register_service
from txmatching.auth.user.user_auth_management import change_user_password, register_user
from txmatching.database.services.app_user_management import get_app_user_by_id


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


def register(email: str, password: str, role: UserRole, second_factor: str):
    """
    Registers new user entity.
    """
    if role == UserRole.SERVICE:
        register_service(email=email, password=password, whitelisted_ip=second_factor)
    else:
        register_user(email=email, password=password, role=role, phone_number=second_factor)
