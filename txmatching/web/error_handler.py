# pylint: disable=unused-variable
# because they are registered using annotation
import logging

from dacite import DaciteError
from flask_restx import Api
from werkzeug.exceptions import HTTPException

from txmatching.auth.exceptions import (CredentialsMismatchException,
                                        InvalidArgumentException,
                                        InvalidAuthCallException,
                                        InvalidIpAddressAccessException,
                                        InvalidJWTException,
                                        InvalidOtpException,
                                        UserUpdateException,
                                        CouldNotSendOtpUsingSmsServiceException)

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
    def handle_invalid_jwt_exception(error: InvalidJWTException):
        _log_warning(error)
        return {'error': 'Authentication denied.', 'detail': 'Invalid JWT.'}, 401

    @api.errorhandler(CredentialsMismatchException)
    def handle_credentials_mismatch_exception(error: CredentialsMismatchException):
        _log_warning(error)
        return {'error': 'Authentication denied.', 'detail': 'Credentials mismatch.'}, 401

    @api.errorhandler(InvalidOtpException)
    def handle_invalid_otp_exception(error: InvalidOtpException):
        _log_warning(error)
        return {'error': 'Authentication denied.', 'detail': 'Invalid OTP.'}, 401

    @api.errorhandler(CouldNotSendOtpUsingSmsServiceException)
    def handle_could_not_send_otp(error: CouldNotSendOtpUsingSmsServiceException):
        _log_exception(error)
        return {
                   'error': 'Service unavailable.',
                   'detail': 'It was not possible to reach the SMS gate. Please contact support.'
               }, 503

    @api.errorhandler(InvalidIpAddressAccessException)
    def handle_invalid_ip_exception(error: InvalidIpAddressAccessException):
        _log_warning(error)
        return {'error': 'Authentication denied.', 'detail': 'Used IP is not whitelisted.'}, 401

    @api.errorhandler(UserUpdateException)
    def handle_user_update_exception(error: UserUpdateException):
        logger.warning(f'It was not possible to update user. - {repr(error)}')
        _log_warning(error)
        return {'error': 'Invalid data submitted.', 'detail': str(error)}, 400

    @api.errorhandler(InvalidAuthCallException)
    def handle_invalid_auth_call_exception(error: InvalidAuthCallException):
        _log_warning(error)
        return {'error': 'Internal error, please contact support.', 'detail': str(error)}, 500

    @api.errorhandler(InvalidArgumentException)
    def handle_invalid_argument_exception(error: InvalidArgumentException):
        _log_warning(error)
        return {'error': 'Invalid argument.', 'detail': str(error)}, 400

    @api.errorhandler(DaciteError)
    def handle_dacite_exception(error: DaciteError):
        _log_warning(error)
        return {'error': 'Invalid request data.', 'detail': str(error)}, 400

    @api.errorhandler(ValueError)
    def handle_invalid_value_error(error: ValueError):
        _log_warning(error)
        return {'error': 'Invalid argument.', 'detail': str(error)}, 400


def _default_error_handlers(api: Api):
    """
    Registers default top level handlers, must be registered last.
    """

    @api.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        _log_exception(error)
        return {'error': error.name, 'detail': error.description}, _get_code_from_error_else_500(error)

    @api.errorhandler(Exception)
    def handle_default_exception_error(error: Exception):
        _log_exception(error)
        return {'error': 'Internal server error', 'detail': str(error)}, _get_code_from_error_else_500(error)

    @api.errorhandler
    def handle_default_error(error):
        _log_exception(error)
        return {'error': error.name, 'detail': error.description}, _get_code_from_error_else_500(error)


def _log_exception(ex: Exception):
    logger.exception(_format_exception(ex))


def _log_warning(ex: Exception):
    logger.warning(_format_exception(ex))


def _format_exception(ex: Exception) -> str:
    return f'{type(ex)}: - {str(ex)}'


def _get_code_from_error_else_500(error: Exception):
    error_code = getattr(error, 'code', 500)
    if isinstance(error_code, int):
        logger.error(f'Unexpected error code returned {error_code}, returning 500 instead')
        return error_code
    return 500
