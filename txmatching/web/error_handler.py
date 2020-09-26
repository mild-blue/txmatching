import logging

from flask_restx import Api
from werkzeug.exceptions import HTTPException

from txmatching.auth.exceptions import InvalidJWTException, CredentialsMismatchException, InvalidOtpException, \
    InvalidIpAddressAccessException, UserUpdateException

logger = logging.getLogger(__name__)


def register_error_handlers(api: Api):
    """
    Registers error handlers in the application.

    Note that it depends on the order of the handlers.
    """
    _user_auth_handlers(api)
    _default_error_handlers(api)


def _user_auth_handlers(api: Api):
    @api.errorhandler(InvalidJWTException)
    def handle_invalid_jwt(error: InvalidJWTException):
        logger.warning(f'Invalid JWT used. - {repr(error)}')
        return {'error': 'Authentication denied.', 'detail': 'Invalid JWT.'}, 401

    @api.errorhandler(CredentialsMismatchException)
    def handle_credentials_mismatch(error: CredentialsMismatchException):
        logger.warning(f'Credentials do not match. - {repr(error)}')
        return {'error': 'Authentication denied.', 'detail': 'Credentials mismatch.'}, 401

    @api.errorhandler(InvalidOtpException)
    def handle_invalid_otp(error: InvalidOtpException):
        logger.warning(f'Invalid OTP used. - {repr(error)}')
        return {'error': 'Authentication denied.', 'detail': 'Invalid OTP.'}, 401

    @api.errorhandler(InvalidIpAddressAccessException)
    def handle_invalid_ip(error: InvalidIpAddressAccessException):
        logger.warning(f'IP not on whitelist. - {repr(error)}')
        return {'error': 'Authentication denied.', 'detail': 'Used IP is not on whitelist.'}, 401

    @api.errorhandler(UserUpdateException)
    def handle_root_exception(error: UserUpdateException):
        logger.warning(f'It was not possible to update user. - {repr(error)}')
        return {'error': 'Invalid data submitted.', 'detail': str(error)}, 400


def _default_error_handlers(api: Api):
    """
    Registers default top level handlers, must be registered last.
    """

    @api.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        logger.warning(f'HttpException: - {repr(error)}')
        return {'error': error.name, 'detail': error.description}, getattr(error, 'code', 500)

    @api.errorhandler(Exception)
    def default_error_handler(error: Exception):
        logger.exception(error)
        return {'error': 'Internal server error', 'detail': str(error)}, getattr(error, 'code', 500)

    @api.errorhandler
    def default_error_handler(error):
        logger.warning(f'Error: - {repr(error)}')
        return {'error': error.name, 'detail': error.description}, getattr(error, 'code', 500)
