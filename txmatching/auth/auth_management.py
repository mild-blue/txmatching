from txmatching.auth.data_types import UserRole, TokenType
from txmatching.auth.exceptions import require_auth_condition
from txmatching.auth.request_context import get_request_token
from txmatching.auth.service.service_auth_management import register_service
from txmatching.auth.user.user_auth_management import change_user_password, register_user


def change_password(new_password: str):
    """
    Changes password for the current user.
    """
    request_token = get_request_token()
    require_auth_condition(request_token.role != UserRole.SERVICE,
                           f'{request_token.role} is not allowed to change the password!')
    require_auth_condition(request_token.type != TokenType.OTP,
                           f'{request_token.type} is not enough to change the password!')

    change_user_password(request_token.user_id, new_password)


def register(email: str, password: str, role: UserRole, second_factor: str):
    """
    Registers new user entity.
    """
    if role == UserRole.SERVICE:
        register_service(email=email, password=password, whitelisted_ip=second_factor)
    else:
        register_user(email=email, password=password, role=role, phone_number=second_factor)
