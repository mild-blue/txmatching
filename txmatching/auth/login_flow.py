import logging

from flask import request

from txmatching.auth.crypto.jwt_crypto import encode_auth_token
from txmatching.auth.crypto.password_crypto import password_matches_hash
from txmatching.auth.data_types import UserRole, TokenType, BearerTokenRequest, EncodedBearerToken
from txmatching.auth.exceptions import CredentialsMismatchException
from txmatching.auth.request_context import get_request_token
from txmatching.auth.service.service_auth import service_login_flow
from txmatching.auth.user.user_auth import user_login_flow, refresh_user_token, user_otp_login
from txmatching.configuration.app_configuration.application_configuration import get_application_configuration, \
    ApplicationConfiguration
from txmatching.database.services.app_user_management import get_app_user_by_email, get_app_user_by_id

# asserts are here just to be sure
# it should be handled by the controllers
# but as this is auth, we want to be 100% sure

logger = logging.getLogger(__name__)


def credentials_login(email: str, password: str) -> str:
    """
    Starts login flow for the given credentials. Returns valid JWT,
    if verification fails, some AuthenticationException is raised.
    """
    user = get_app_user_by_email(email.lower())
    if not user or not password_matches_hash(user.pass_hash, password):
        raise CredentialsMismatchException()

    conf = get_application_configuration()

    if user.role == UserRole.SERVICE:
        token = service_login_flow(user, request.remote_addr)
    else:
        token = user_login_flow(user, conf.jwt_expiration_days)

    return _encode_auth_token(token, conf.jwt_secret)


def refresh_token() -> str:
    """
    Refreshes JWT for users, does not work for SERVICE accounts and OTP tokens.
    """
    return _refresh_token(get_request_token(), get_application_configuration())


def _refresh_token(request_token: EncodedBearerToken, conf: ApplicationConfiguration) -> str:
    assert request_token.role != UserRole.SERVICE
    assert request_token.type != TokenType.OTP

    new_token = refresh_user_token(request_token, conf.jwt_expiration_days)
    return _encode_auth_token(new_token, conf.jwt_secret)


def otp_login(otp: str) -> str:
    """
    Validates OTP and issues ACCESS token for full access.
    """
    return _otp_login(otp, get_request_token(), get_application_configuration())


def _otp_login(otp: str, request_token: EncodedBearerToken, conf: ApplicationConfiguration) -> str:
    assert request_token.role != UserRole.SERVICE
    assert request_token.type == TokenType.OTP

    user = get_app_user_by_id(request_token.user_id)
    assert user is not None

    access_token = user_otp_login(user, otp, conf.jwt_expiration_days)
    return _encode_auth_token(access_token, conf.jwt_secret)


def _encode_auth_token(token_request: BearerTokenRequest, jwt_secret: str) -> str:
    return encode_auth_token(
        user_id=token_request.user_id,
        user_role=token_request.role,
        token_type=token_request.type,
        expiration=token_request.expiration,
        jwt_secret=jwt_secret
    )
