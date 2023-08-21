from typing import Optional


class BaseTxmException(Exception):
    """
    Base class for TXM related exceptions.
    """


class NotFoundException(BaseTxmException):
    """
    Something was not found (probably something in the database).
    """


class AuthenticationException(BaseTxmException):
    """
    Base class for Authentication related exceptions.
    """


class InvalidJWTException(AuthenticationException):
    """
    Exception indicating that JWT is invalid for some reason.
    """


class CredentialsMismatchException(AuthenticationException):
    """
    Email and password don't match.
    """


class InvalidOtpException(AuthenticationException):
    """
    Used OTP is no longer valid.
    """


class InvalidIpAddressAccessException(AuthenticationException):
    """
    IP address of the service account was not whitelisted.
    """

    def __init__(self, ip_address: str = 'Unknown', message: str = ''):
        self.ip_address = ip_address
        super().__init__(message)


class UserUpdateException(AuthenticationException):
    """
    Raised if the registration or update of the user fails.
    """


class InvalidAuthCallException(AuthenticationException):
    """
    Raised if the code started executing unexpected flow.
    """


class CouldNotSendOtpUsingSmsServiceException(AuthenticationException):
    """
    Raised if the SMS service could not be reached or responded with
    unexpected status code. In that case OTP code was not sent.
    """


class GuardException(AuthenticationException):
    """
    Raised if some guard does not allow the perform the operation.
    """


class WrongTokenUsedException(AuthenticationException):
    """
    Raised if wrong token type was used.
    """


class InvalidTokenException(AuthenticationException):
    """
    Raised if invalid token was used.
    """


class InvalidEmailException(AuthenticationException):
    """
    Raised if invalid email was used.
    """


class InvalidArgumentException(BaseTxmException):
    """
    Raised if invalid argument received.
    """
    def __init__(self, message: str = 'Invalid argument.'):
        self.message = message
        super().__init__(self.message)


class TooComplicatedDataForAllSolutionsSolver(BaseTxmException):
    """
    Raised if invalid argument received.
    """


class CannotFindShortEnoughRoundsOrPathsInILPSolver(BaseTxmException):
    """
    Raised if there are too many possible paths and rounds longer than the threshold. And by adding dynamic constraints
    we are not able to narrow the length of the paths down enough.
    """

    default_message = """
    There are too many possible solutions for the provided set of patients and the algorithm cannot find the optimal
    solution with the provided configuration. Try changing the configuration, ideally in the following order: increase
    the number of dynamic constraints, increase the max length of cycle/sequence, increase the max number of countries
    in round.

    If you need help, contact administrators at info@mild.blue or +420 723 927 536.

    This is happening because the algorithm is still under development. We are working intensively to ensure that this
    is not necessary in the future.
    """
    def __init__(self, message: str = default_message):
        self.message = message
        super().__init__(self.message)

class SolverAlreadyRunningException(BaseTxmException):
    """
    Indicates that the Solver is already running and TXM can not start it again.
    """


class UnauthorizedException(BaseTxmException):
    """
    Raised if user tries to access resource he has no access to.
    """
    def __init__(self, message: str = 'Not authorized.'):
        self.message = message
        super().__init__(self.message)

class OverridingException(BaseTxmException):
    """
    Raised if user tries to override a patient.
    """


class NonUniquePatient(BaseTxmException):
    """
    Non-unique patients provided.
    # created for swagger documentation.
    """


class TXMNotImplementedFeatureException(BaseTxmException):
    """
    Functionality is not implemented yet. Just inform user about this situation.
    This exception is completely OK and should be loged with level INFO.
    Do not confuse with python NotImplementedError (corresponds to unexpected internal errors with code 500).
    """


class CPRACalculationBaseException(Exception):
    """
    Base class for CPRA calculation with http://ETRL.ORG/ related exceptions.
    """


class ETRLRequestException(CPRACalculationBaseException):
    """
    The request from the http://ETRL.ORG/ was not successful.
    """


class ETRLErrorResponse(CPRACalculationBaseException):
    """
    There is an error in the response from the http://ETRL.ORG/.
    """


def require_auth_condition(condition: bool, message: Optional[str] = None):
    """
    Raises InvalidAuthCallException with message if condition is false.
    """
    if not condition:
        raise InvalidAuthCallException(message)
