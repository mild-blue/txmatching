# pylint: disable=unused-variable
# because they are registered using annotation
import logging

from dacite import DaciteError
from flask_restx import Api, Namespace, fields
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
        """Solver is already running"""
        _log_warning(error)
        return {'error': 'Solver already running.',
                'message': 'The solver is running right now, try again in few minutes.'}, 423

    @api.errorhandler(InvalidJWTException)
    def handle_invalid_jwt_exception(error: InvalidJWTException):
        """Invalid JWT exception"""
        _log_warning(error)
        return {'error': 'Authentication failed.', 'message': 'Invalid JWT.'}, 401

    @api.errorhandler(NotFoundException)
    @_namespace_error_response(code=404)
    def handle_not_found_exception(error: NotFoundException):
        """
        Matching not found.
        / Not Found
        """
        _log_warning(error)
        return {'error': 'Not Found', 'message': str(error)}, 404

    @api.errorhandler(CredentialsMismatchException)
    def handle_credentials_mismatch_exception(error: CredentialsMismatchException):
        """Credentials Mismatch Exception"""
        _log_warning(error)
        return {'error': 'Authentication failed.', 'message': 'Credentials mismatch.'}, 401

    @api.errorhandler(InvalidOtpException)
    @_namespace_error_response(code=401)
    def handle_invalid_otp_exception(error: InvalidOtpException):
        """
        Authentication failed.
        Invalid Otp Exception
        """
        _log_warning(error)
        return {'error': 'Authentication failed.', 'message': 'Invalid OTP.'}, 401

    @api.errorhandler(CouldNotSendOtpUsingSmsServiceException)
    @_namespace_error_response(code=503)
    def handle_could_not_send_otp(error: CouldNotSendOtpUsingSmsServiceException):
        """
        Service(s) is unavailable.
        Could not send Otp
        """
        _log_exception(error)
        return {
            'error': 'SMS service unavailable.',
            'message': 'It was not possible to reach the SMS gate. Please contact support.'
        }, 503

    @api.errorhandler(InvalidIpAddressAccessException)
    def handle_invalid_ip_exception(error: InvalidIpAddressAccessException):
        """Invalid IP"""
        _log_warning(error)
        return {'error': 'Authentication failed.', 'message': f'Used IP {error.ip_address} is not whitelisted.'}, 401

    @api.errorhandler(UserUpdateException)
    def handle_user_update_exception(error: UserUpdateException):
        """User update exception"""
        _log_warning(error)
        return {'error': 'Invalid data submitted.', 'message': str(error)}, 400

    @api.errorhandler(InvalidAuthCallException)
    @_namespace_error_response(code=500)
    def handle_invalid_auth_call_exception(error: InvalidAuthCallException):
        """
        Internal error.
        Invalid auth call exception
        """
        _log_warning(error)
        return {'error': 'Internal error, please contact support.', 'message': str(error)}, 500

    @api.errorhandler(GuardException)
    def handle_guard_exception(error: GuardException):
        """Guard exception"""
        _log_warning(error)
        return {'error': 'Access denied.', 'message': str(error)}, 403

    @api.errorhandler(WrongTokenUsedException)
    def handle_wrong_used_token_exception(error: WrongTokenUsedException):
        """Wrong used token exception"""
        _log_warning(error)
        return {'error': 'Authentication denied. Wrong token used.', 'message': str(error)}, 403

    @api.errorhandler(InvalidTokenException)
    def handle_invalid_token_exception(error: InvalidTokenException):
        """Invalid token exception"""
        _log_warning(error)
        return {'error': 'Authentication failed.', 'message': str(error)}, 403

    @api.errorhandler(InvalidEmailException)
    def handle_invalid_email_exception(error: InvalidEmailException):
        """Invalid email exception"""
        _log_warning(error)
        return {'error': 'Authentication failed.', 'message': str(error)}, 403

    @api.errorhandler(AuthenticationException)
    @_namespace_error_response(code=403)
    def handle_general_authentication_exception(error: AuthenticationException):
        """
        Access denied.
        General authentication exception
        """
        _log_warning(error)
        return {'error': 'Access denied', 'message': str(error)}, 403

    @api.errorhandler(InvalidArgumentException)
    def handle_invalid_argument_exception(error: InvalidArgumentException):
        """Invalid argument exception"""
        _log_warning(error)
        return {'error': error.message, 'message': str(error)}, 400

    @api.errorhandler(UnauthorizedException)
    def handle_unauthorized_exception(error: UnauthorizedException):
        """Unauthorized"""
        _log_warning(error)
        return {'error': error.message, 'message': str(error)}, 403

    @api.errorhandler(TooComplicatedDataForAllSolutionsSolver)
    def handle_too_complicated_data_for_solver_exception(error: TooComplicatedDataForAllSolutionsSolver):
        """Too complicated data for solver"""
        _log_warning(error)
        return {'error': 'The solution for this combination of patients and configuration '
                         'is too complicated for AllSolutionsSolver, please use ILPSolver.', 'message': str(error)}, 400

    @api.errorhandler(CannotFindShortEnoughRoundsOrPathsInILPSolver)
    def handle_too_complicated_data_for_ilp_solver_exception(error: CannotFindShortEnoughRoundsOrPathsInILPSolver):
        """Too complicated data for solver"""
        _log_warning(error)
        return {'error': error.message, 'message': str(error)}, 400

    @api.errorhandler(DaciteError)
    def handle_dacite_exception(error: DaciteError):
        """Dacite Exception"""
        _log_warning(error)
        return {'error': 'Invalid request data.', 'message': str(error)}, 400

    @api.errorhandler(KeyError)
    @_namespace_error_response(code=400)
    def handle_key_error(error: KeyError):
        """
        Wrong data format.
        Key Error
        """
        _log_warning(error)
        return {'error': 'Invalid request data.', 'message': str(error)}, 400

    @api.errorhandler(ValueError)
    def handle_value_error(error: ValueError):
        """Value Error"""
        _log_warning(error)
        return {'error': 'Invalid request data.', 'message': str(error)}, 400

    @api.errorhandler(Forbidden)
    def handle_access_denied(error: Forbidden):
        """Access denied"""
        _log_warning(error)
        return {'error': 'Access denied', 'message': str(error.description)}, error.code

    @api.errorhandler(OverridingException)
    def handle_not_acceptable_exception(error: OverridingException):
        """Not acceptable exception"""
        _log_warning(error)
        return {'error': 'The patient can\'t be updated, someone edited this patient in the meantime. ' +
                'You have to reload the patient first. The changes will be lost.', 'message': str(error)}, 406

    @_namespace_error_response(code=409)
    def handle_non_unique_patient():
        """
        Non-unique patients provided.
        # Created for namespace error response.
        """


def _namespace_error_response(code):
    """
    Decorator marks, that handle-function's __doc__ will be used as error response.
    Use it for handle-functions in _user_auth_handlers().
    If possible, only the second line of the docstring will be used for the response.

    Examples:
    1.      '''
            Authentication failed.                    <--- only this line will be used for response
            General authentication exception.
            '''

    2.      ''' Access denied. '''                    <--- this line will be used for response

    :param code: error response's code
    Responses are saved as Namespace._ERROR_RESPONSES.
    """
    # noinspection PyProtectedMember
    def inner(func):
        splitted_doc = func.__doc__.split('\n')
        Namespace._ERROR_RESPONSES[code] = splitted_doc[1].strip() if len(splitted_doc) > 1 \
            else func.__doc__
        return func

    return inner


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


# for filling responses by @_namespace_error_response in handlers
Namespace._ERROR_RESPONSES = {501: f"This response is not implemented by error-handler. "
                                   f"Mark needed exception using "
                                   f"'@_namespace_error_response(code=CODE)' "
                                   f"in {__file__}.{_user_auth_handlers.__name__}"}


def _generate_namespace_error_responses():
    """
    Activates decorator @_namespace_error_responses
    to fill Namespace._ERROR_RESPONSES by handlers __doc__.
    Call it during NamespaceWithErrorResponses definition.
    """
    FakeApi = Api()
    _user_auth_handlers(FakeApi)


# noinspection PyProtectedMember
class NamespaceWithErrorResponses(Namespace):
    """ flask_restx.Namespace with error responses. """

    # creating error responses by code in Namespace._ERROR_RESPONSES
    _generate_namespace_error_responses()

    def _create_fail_response_model(self):
        return self.model('FailResponse', {
            'error': fields.String(required=True),
            'message': fields.String(required=False),
        })

    def response_error_matching_not_found(self):
        code = 404 if 404 in Namespace._ERROR_RESPONSES.keys() else 501
        model = self._create_fail_response_model()
        return self.response(code=code, model=model,
                             description=Namespace._ERROR_RESPONSES[code])

    def response_error_non_unique_patients_provided(self):
        code = 409 if 409 in Namespace._ERROR_RESPONSES.keys() else 501
        model = self._create_fail_response_model()
        return self.response(code=code, model=model,
                             description=Namespace._ERROR_RESPONSES[code])

    def response_error_unexpected(self):
        code = 500 if 500 in Namespace._ERROR_RESPONSES.keys() else 501
        model = self._create_fail_response_model()
        return self.response(code=code, model=model,
                             description=Namespace._ERROR_RESPONSES[code])

    def response_error_services_failing(self):
        code = 503 if 503 in Namespace._ERROR_RESPONSES.keys() else 501
        model = self._create_fail_response_model()
        return self.response(code=code, model=model,
                             description=Namespace._ERROR_RESPONSES[code])

    def response_error_sms_gate(self):
        return self.response_error_services_failing()

    def response_error_wrong_data(self):
        code = 400 if 400 in Namespace._ERROR_RESPONSES.keys() else 501
        model = self._create_fail_response_model()
        return self.response(code=code, model=model,
                             description=Namespace._ERROR_RESPONSES[code])

    def response_error_unauthorized(self):
        code = 401 if 401 in Namespace._ERROR_RESPONSES.keys() else 501
        model = self._create_fail_response_model()
        return self.response(code=code, model=model,
                             description=Namespace._ERROR_RESPONSES[code])

    def response_error_forbidden(self):
        code = 403 if 403 in Namespace._ERROR_RESPONSES.keys() else 501
        model = self._create_fail_response_model()
        return self.response(code=code, model=model,
                             description=Namespace._ERROR_RESPONSES[code])


def _log_exception(ex: Exception):
    logger.exception(_format_exception(ex))


def _log_warning(ex: Exception):
    logger.warning(_format_exception(ex))


def _log_unexpected_error(error_code: int):
    logger.error(f'Unexpected error code returned {error_code}, returning 500 instead')


def _format_exception(ex: Exception) -> str:
    return f'{type(ex)}: - {str(ex)}'


def _get_code_from_error_else_500(error: Exception):
    error_code = getattr(error, 'code', 500)
    if isinstance(error_code, int):
        _log_unexpected_error(error_code)
        return error_code
    return 500
