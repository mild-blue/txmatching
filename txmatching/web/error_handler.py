# pylint: disable=unused-variable
# because they are registered using annotation
import logging

from dacite import DaciteError
from flask_restx import Api
from werkzeug.exceptions import Forbidden, HTTPException

from txmatching.auth.exceptions import (
    AuthenticationException, CannotFindShortEnoughRoundsOrPathsInILPSolver,
    CouldNotSendOtpUsingSmsServiceException, CredentialsMismatchException,
    GuardException, InvalidArgumentException, InvalidAuthCallException,
    InvalidEmailException, InvalidIpAddressAccessException,
    InvalidJWTException, InvalidOtpException, InvalidTokenException, OverridingException,
    NotFoundException, SolverAlreadyRunningException,
    TooComplicatedDataForAllSolutionsSolver, UnauthorizedException,
    UserUpdateException, WrongTokenUsedException)
from txmatching.configuration.app_configuration.application_configuration import (
    ApplicationEnvironment, get_application_configuration)

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
    @api.errorhandler(SolverAlreadyRunningException)
    def handle_solver_already_running_exception(error: SolverAlreadyRunningException):
        """Solver already running"""
        _log_warning(error)
        return {'error': 'Solver already running.',
                'message': 'The solver is running right now, try again in few minutes.'}, 423

    @api.errorhandler(InvalidJWTException)
    def handle_invalid_jwt_exception(error: InvalidJWTException):
        """invalid_jwt_exception"""
        _log_warning(error)
        return {'error': 'Authentication failed.', 'message': 'Invalid JWT.'}, 401

    @api.errorhandler(NotFoundException)
    def handle_not_found_exeption(error: NotFoundException):
        """not_found_exception"""
        _log_warning(error)
        return {'error': 'Not Found', 'message': str(error)}, 401

    @api.errorhandler(CredentialsMismatchException)
    def handle_credentials_mismatch_exception(error: CredentialsMismatchException):
        """credentials_mismatch_exception"""
        _log_warning(error)
        return {'error': 'Authentication failed.', 'message': 'Credentials mismatch.'}, 401

    @api.errorhandler(InvalidOtpException)
    def handle_invalid_otp_exception(error: InvalidOtpException):
        """invalid_otp_exception"""
        _log_warning(error)
        return {'error': 'Authentication failed.', 'message': 'Invalid OTP.'}, 401

    @api.errorhandler(CouldNotSendOtpUsingSmsServiceException)
    def handle_could_not_send_otp(error: CouldNotSendOtpUsingSmsServiceException):
        """could_not_send_otp"""
        _log_exception(error)
        return {
            'error': 'SMS service unavailable.',
            'message': 'It was not possible to reach the SMS gate. Please contact support.'
        }, 503

    @api.errorhandler(InvalidIpAddressAccessException)
    def handle_invalid_ip_exception(error: InvalidIpAddressAccessException):
        """invalid_ip_exception"""
        _log_warning(error)
        return {'error': 'Authentication failed.', 'message': f'Used IP {error.ip_address} is not whitelisted.'}, 401

    @api.errorhandler(UserUpdateException)
    def handle_user_update_exception(error: UserUpdateException):
        """user_update_exception"""
        _log_warning(error)
        return {'error': 'Invalid data submitted.', 'message': str(error)}, 400

    @api.errorhandler(InvalidAuthCallException)
    def handle_invalid_auth_call_exception(error: InvalidAuthCallException):
        """invalid_auth_call_exception"""
        _log_warning(error)
        return {'error': 'Internal error, please contact support.', 'message': str(error)}, 500

    @api.errorhandler(GuardException)
    def handle_guard_exception(error: GuardException):
        """guard_exception"""
        _log_warning(error)
        return {'error': 'Access denied.', 'message': str(error)}, 403

    @api.errorhandler(WrongTokenUsedException)
    def handle_wrong_used_token_exception(error: WrongTokenUsedException):
        """wrong_used_token_exception"""
        _log_warning(error)
        return {'error': 'Authentication denied. Wrong token used.', 'message': str(error)}, 403

    @api.errorhandler(InvalidTokenException)
    def handle_invalid_token_exception(error: InvalidTokenException):
        """invalid_token_exception"""
        _log_warning(error)
        return {'error': 'Authentication failed.', 'message': str(error)}, 403

    @api.errorhandler(InvalidEmailException)
    def handle_invalid_email_exception(error: InvalidEmailException):
        """invalid_email_exception"""
        _log_warning(error)
        return {'error': 'Authentication failed.', 'message': str(error)}, 403

    @api.errorhandler(AuthenticationException)
    def handle_general_authentication_exception(error: AuthenticationException):
        """general_authentication_exception"""
        _log_warning(error)
        return {'error': 'Access denied', 'message': str(error)}, 403

    @api.errorhandler(InvalidArgumentException)
    def handle_invalid_argument_exception(error: InvalidArgumentException):
        """invalid_argument_exception"""
        _log_warning(error)
        return {'error': error.message, 'message': str(error)}, 400

    @api.errorhandler(UnauthorizedException)
    def handle_unauthorized_exception(error: UnauthorizedException):
        """unauthorized_exception"""
        _log_warning(error)
        return {'error': error.message, 'message': str(error)}, 403

    @api.errorhandler(TooComplicatedDataForAllSolutionsSolver)
    def handle_too_complicated_data_for_solver_exception(error: TooComplicatedDataForAllSolutionsSolver):
        """too complicated data for solver _exception"""
        _log_warning(error)
        return {'error': 'The solution for this combination of patients and configuration '
                         'is too complicated for AllSolutionsSolver, please use ILPSolver.', 'message': str(error)}, 400

    @api.errorhandler(CannotFindShortEnoughRoundsOrPathsInILPSolver)
    def handle_too_complicated_data_for_ilp_solver_exception(error: CannotFindShortEnoughRoundsOrPathsInILPSolver):
        """too complicated data for solver _exception"""
        _log_warning(error)
        return {'error': error.message, 'message': str(error)}, 400

    @api.errorhandler(DaciteError)
    def handle_dacite_exception(error: DaciteError):
        """dacite_exception"""
        _log_warning(error)
        return {'error': 'Invalid request data.', 'message': str(error)}, 400

    @api.errorhandler(KeyError)
    def handle_key_error(error: KeyError):
        """key_error"""
        _log_warning(error)
        return {'error': 'Invalid request data.', 'message': str(error)}, 400

    @api.errorhandler(ValueError)
    def handle_value_error(error: ValueError):
        """value_error"""
        _log_warning(error)
        return {'error': 'Invalid request data.', 'message': str(error)}, 400

    @api.errorhandler(Forbidden)
    def handle_access_denied(error: Forbidden):
        """access_denied"""
        _log_warning(error)
        return {'error': 'Access denied', 'message': str(error.description)}, error.code

    @api.errorhandler(OverridingException)
    def handle_not_acceptable_exception(error: OverridingException):
        """not_acceptable_exception"""
        _log_warning(error)
        return {'error': 'The patient can\'t be updated, someone edited this patient in the meantime. ' +
                'You have to reload the patient first. The changes will be lost.', 'message': str(error)}, 406


def _default_error_handlers(api: Api):
    """
    Registers default top level handlers, must be registered last.
    """
    is_prod = get_application_configuration().environment == ApplicationEnvironment.PRODUCTION

    def strip_on_prod(description: str):
        return description if not is_prod else 'An unknown error occurred. Contact administrator.'

    @api.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """http_exception"""
        _log_exception(error)
        return {
            'error': error.name,
            'message': strip_on_prod(str(error))
        }, _get_code_from_error_else_500(error)

    @api.errorhandler(Exception)
    def handle_default_exception_error(error: Exception):
        """default_exception_error"""
        _log_exception(error)
        return {
            'error': 'Internal server error',
            'message': strip_on_prod(str(error))
        }, _get_code_from_error_else_500(error)

    @api.errorhandler
    def handle_default_error(error):
        """default_error"""
        _log_exception(error)
        return {
            'error': error.name,
            'message': strip_on_prod(error.description)
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
