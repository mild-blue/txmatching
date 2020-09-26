import datetime
import logging

from txmatching.auth.data_types import BearerTokenRequest, UserRole, TokenType, EncodedBearerToken
from txmatching.auth.exceptions import InvalidOtpException
from txmatching.auth.user.totp import OTP_LIVENESS_MINUTES, generate_otp_for_user, verify_otp_for_user
from txmatching.database.sql_alchemy_schema import AppUserModel

logger = logging.getLogger(__name__)


def user_login_flow(user: AppUserModel, jwt_expiration_days: int) -> BearerTokenRequest:
    """
    Issues temporary JWT and sends OTP code for further verification.
    """
    assert user.role != UserRole.SERVICE

    if user.require_2fa:
        otp = generate_otp_for_user(user)
        _send_sms_otp(otp, user)
        token = BearerTokenRequest(
            user_id=user.id,
            role=user.role,
            type=TokenType.OTP,
            expiration=datetime.timedelta(minutes=OTP_LIVENESS_MINUTES)
        )
    else:
        token = BearerTokenRequest(
            user_id=user.id,
            role=user.role,
            type=TokenType.ACCESS,
            expiration=datetime.timedelta(days=jwt_expiration_days)
        )
    return token


def user_otp_login(user: AppUserModel, otp: str, jwt_expiration_days: int) -> BearerTokenRequest:
    """
    Validates OTP and creates request for bearer.
    """
    assert user.role != UserRole.SERVICE

    if not verify_otp_for_user(user, otp):
        raise InvalidOtpException(f'OTP is not valid for the user {user.email}')

    return BearerTokenRequest(
        user_id=user.id,
        role=user.role,
        type=TokenType.ACCESS,
        expiration=datetime.timedelta(days=jwt_expiration_days)
    )


def refresh_user_token(token: EncodedBearerToken, jwt_expiration_days: int) -> BearerTokenRequest:
    """"
    Generates new JWT with extended lifespan.
    """
    assert token.type == TokenType.ACCESS
    assert token.role != UserRole.SERVICE

    return BearerTokenRequest(
        user_id=token.user_id,
        role=token.role,
        type=token.type,
        expiration=datetime.timedelta(days=jwt_expiration_days)
    )


def _send_sms_otp(otp: str, user: AppUserModel):
    assert user.phone_number is not None
    assert otp
    # TODO send the OTP to the user
    logger.info(f'OTP issued: "{otp}" for user {user.email}')
