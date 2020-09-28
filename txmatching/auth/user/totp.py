import pyotp

from txmatching.auth.data_types import UserRole
from txmatching.auth.exceptions import require_auth_condition
from txmatching.database.sql_alchemy_schema import AppUserModel

# TODO https://trello.com/c/3RtDcOlt consider putting this to the configuration instead of the code


OTP_VALIDITY_MINUTES = 5
"""
How long is one single OTP considered valid.
"""

OTP_REFRESH_INTERVAL_MINUTES = 1
"""
How often new OTP should be generated.
"""


def generate_totp_seed() -> str:
    """
    Generates seed for the OTP algorithm, seed should be stored per user.
    """
    return pyotp.random_base32()


def generate_otp_for_user(user: AppUserModel) -> str:
    """
    Generates OTP for given user.
    """
    return _totp(user).now()


def verify_otp_for_user(user: AppUserModel, otp: str) -> bool:
    """
    Validates the OTP for the given user.
    Sliding window is determined by the OTP_VALIDITY_MINUTES and OTP_REFRESH_INTERVAL_MINUTES
    """
    return _totp(user).verify(otp, valid_window=int(OTP_VALIDITY_MINUTES / OTP_REFRESH_INTERVAL_MINUTES))


def _totp(user: AppUserModel) -> pyotp.TOTP:
    require_auth_condition(user.role != UserRole.SERVICE, f'TOTP request for {user.role}!')
    return pyotp.TOTP(user.second_factor_material, interval=OTP_REFRESH_INTERVAL_MINUTES * 60)
