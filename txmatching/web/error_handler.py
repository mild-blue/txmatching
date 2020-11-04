# pylint: disable=unused-variable
# because they are registered using annotation
import logging

from dacite import DaciteError
from flask_restx import Api
from werkzeug.exceptions import Forbidden, HTTPException

from txmatching.auth.exceptions import (
    AuthenticationException, CouldNotSendOtpUsingSmsServiceException,
    CredentialsMismatchException, GuardException, InvalidArgumentException,
    InvalidAuthCallException, InvalidIpAddressAccessException,
    InvalidJWTException, InvalidOtpException, UserUpdateException,
    WrongTokenException)
from txmatching.configuration.app_configuration.application_configuration import \
    get_application_configuration

logger = logging.getLogger(__name__)


def register_error_handlers(api: Api):
    """
    Registers error handlers in the application.

    Note that it depends on the order of the handlers.
    """
    _user_auth_handlers(api)
    _default_error_handlers(api)


# pylint: disable=too-many-locals
# it is valid to have here all the possible handlers, even if they are many
def _user_auth_handlers(api: Api):
    @api.errorhandler(InvalidJWTException)
    def handle_invalid_jwt_exception(error: InvalidJWTException):
        """invalid jwt exception"""
        _log_warning(error)
        return {'error': 'Authentication failed.', 'detail': 'Invalid JWT.'}, 401

    @api.errorhandler(CredentialsMismatchException)
    def handle_credentials_mismatch_exception(error: CredentialsMismatchException):
        """handle_credentials_mismatch_exception"""
        _log_warning(error)
        return {'error': 'Authentication failed.', 'detail': 'Credentials mismatch.'}, 401

    @api.errorhandler(InvalidOtpException)
    def handle_invalid_otp_exception(error: InvalidOtpException):
        """handle_invalid_otp_exception"""
        _log_warning(error)
        return {'error': 'Authentication failed.', 'detail': 'Invalid OTP.'}, 401

    @api.errorhandler(CouldNotSendOtpUsingSmsServiceException)
    def handle_could_not_send_otp(error: CouldNotSendOtpUsingSmsServiceException):
        """handle_could_not_send_otp"""
        _log_exception(error)
        return {
                   'error': 'Service unavailable.',
                   'detail': 'It was not possible to reach the SMS gate. Please contact support.'
               }, 503

    @api.errorhandler(InvalidIpAddressAccessException)
    def handle_invalid_ip_exception(error: InvalidIpAddressAccessException):
        """handle_invalid_ip_exception"""
        _log_warning(error)
        return {'error': 'Authentication failed.', 'detail': 'Used IP is not whitelisted.'}, 401

    @api.errorhandler(UserUpdateException)
    def handle_user_update_exception(error: UserUpdateException):
        """handle_user_update_exception"""
        logger.warning(f'It was not possible to update user. - {repr(error)}')
        _log_warning(error)
        return {'error': 'Invalid data submitted.', 'detail': str(error)}, 400

    @api.errorhandler(InvalidAuthCallException)
    def handle_invalid_auth_call_exception(error: InvalidAuthCallException):
        """handle_invalid_auth_call_exception"""
        _log_warning(error)
        return {'error': 'Internal error, please contact support.', 'detail': str(error)}, 500

    @api.errorhandler(GuardException)
    def handle_guard_exception(error: GuardException):
        """handle_guard_exception"""
        _log_warning(error)
        return {'error': 'Access denied.', 'detail': str(error)}, 403

    @api.errorhandler(WrongTokenException)
    def handle_wrong_token_exception(error: WrongTokenException):
        """handle wrong token exception"""
        _log_warning(error)
        return {'error': 'Wrong token.', 'detail': str(error)}, 403

    @api.errorhandler(AuthenticationException)
    def handle_general_authentication_exception(error: AuthenticationException):
        """general authentication exception"""
        _log_warning(error)
        return {'error': 'General authentication exception', 'detail': str(error)}, 403

    @api.errorhandler(InvalidArgumentException)
    def handle_invalid_argument_exception(error: InvalidArgumentException):
        """handle_invalid_argument_exception"""
        _log_warning(error)
        return {'error': 'Invalid argument.', 'detail': str(error)}, 400

    @api.errorhandler(DaciteError)
    def handle_dacite_exception(error: DaciteError):
        """handle_dacite_exception"""
        _log_warning(error)
        return {'error': 'Invalid request data.', 'detail': str(error)}, 400

    @api.errorhandler(KeyError)
    def handle_key_error(error: KeyError):
        """handle_key_error"""
        _log_warning(error)
        return {'error': 'Invalid request data.', 'detail': str(error)}, 400

    @api.errorhandler(ValueError)
    def handle_value_error(error: ValueError):
        """handle_value_error"""
        _log_warning(error)
        return {'error': 'Invalid request data.', 'detail': str(error)}, 400

    @api.errorhandler(Forbidden)
    def handle_access_denied(error: Forbidden):
        """handle_access_denied"""
        _log_warning(error)
        return {'error': 'Access denied', 'detail': str(error.description)}, error.code


def _default_error_handlers(api: Api):
    """
    Registers default top level handlers, must be registered last.
    """
    is_prod = get_application_configuration().is_production

    def strip_on_prod(description):
        return description if not is_prod else 'An unknown error occurred. Contact administrator.'

    @api.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """handle_http_exception"""
        _log_exception(error)
        return {
                   'error': error.name,
                   'detail': strip_on_prod(error.description)
               }, _get_code_from_error_else_500(error)

    @api.errorhandler(Exception)
    def handle_default_exception_error(error: Exception):
        """handle_default_exception_error"""
        _log_exception(error)
        return {
                   'error': 'Internal server error',
                   'detail': strip_on_prod(str(error))
               }, _get_code_from_error_else_500(error)

    @api.errorhandler
    def handle_default_error(error):
        """handle_default_error"""
        _log_exception(error)
        return {
                   'error': error.name,
                   'detail': strip_on_prod(error.description)
               }, _get_code_from_error_else_500(error)


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
