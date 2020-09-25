import datetime

from txmatching.auth.data_types import UserRole, TokenType, BearerTokenRequest
from txmatching.auth.exceptions import InvalidIpAddressAccessException
from txmatching.database.sql_alchemy_schema import AppUserModel

# TODO https://trello.com/c/sRq4nFRv specify with the customer
SERVICE_JWT_EXPIRATION_MINUTES = 5


def service_login_flow(user: AppUserModel, request_ip: str) -> BearerTokenRequest:
    """
    Issues JWT for given service user while checking the IP address of the request,
     only whitelisted IPs are allowed.
    """
    assert user.role == UserRole.SERVICE
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
            f'IP mismatch for account {user.email} registered IP: {user.second_factor_material}, '
            f'used IP: {request_ip}'
        )
