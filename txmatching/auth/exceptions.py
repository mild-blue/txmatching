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
    def __init__(self, ip_address: str, message: str):
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


class InvalidArgumentException(BaseTxmException):
    """
    Raised if invalid argument received.
    """


class TooComplicatedDataForAllSolutionsSolver(BaseTxmException):
    """
    Raised if invalid argument received.
    """


class CannotFindShortEnoughRoundsOrPathsInILPSolver(BaseTxmException):
    """
    Raised if there are too many possible paths and rounds longer than the threshold. And by adding dynamic constraints
    we are not able to narrow the length of the paths down enough.
    """


class SolverAlreadyRunningException(BaseTxmException):
    """
    Indicates that the Solver is already running and TXM can not start it again.
    """


class UnauthorizedException(BaseTxmException):
    """
    Raised if user tries to access resource he has no access to.
    """


def require_auth_condition(condition: bool, message: Optional[str] = None):
    """
    Raises InvalidAuthCallException with message if condition is false.
    """
    if not condition:
        raise InvalidAuthCallException(message)
