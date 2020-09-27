from txmatching.auth.data_types import UserRole, TokenType
from txmatching.auth.request_context import get_request_token
from txmatching.auth.service.service_auth_management import register_service
from txmatching.auth.user.user_auth_management import change_user_password, register_user


def change_password(new_password: str):
    """
    Changes password for the current user.
    """
    request_token = get_request_token()

    assert request_token.role != UserRole.SERVICE
    assert request_token.type != TokenType.OTP

    change_user_password(request_token.user_id, new_password)


def register(email: str, password: str, role: UserRole, second_factor: str):
    """
    Registers new user entity.
    """
    if role == UserRole.SERVICE:
        register_service(email=email.lower(), password=password, whitelisted_ip=second_factor)
    else:
        register_user(email=email.lower(), password=password, role=role, phone_number=second_factor)
