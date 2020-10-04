import datetime

from txmatching.auth.data_types import UserRole, TokenType, BearerTokenRequest
from txmatching.auth.exceptions import InvalidIpAddressAccessException, require_auth_condition
from txmatching.database.sql_alchemy_schema import AppUserModel

SERVICE_JWT_EXPIRATION_MINUTES = 2


def service_login_flow(user: AppUserModel, request_ip: str) -> BearerTokenRequest:
    """
    Issues JWT for given service user while checking the IP address of the request,
     only whitelisted IPs are allowed.
    """
    require_auth_condition(user.role == UserRole.SERVICE, f'{user.role} used for service login!')

    if user.require_2fa:
        _assert_second_factor_material(user, request_ip)

    return BearerTokenRequest(
        user_id=user.id,
        role=UserRole.SERVICE,
        type=TokenType.ACCESS,
        expiration=datetime.timedelta(minutes=SERVICE_JWT_EXPIRATION_MINUTES)
    )


def _assert_second_factor_material(user: AppUserModel, request_ip: str):
    """
    Checks IP address of the request, only whitelisted IPs are allowed.
    """
    if user.second_factor_material != request_ip:
        raise InvalidIpAddressAccessException(
            f'IP mismatch for account {user.email}. Registered IP: {user.second_factor_material}, '
            f'used IP: {request_ip}.'
        )
