from typing import Optional


class BaseTxmException(Exception):
    """
    Base class for TXM related exceptions.
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


class UserUpdateException(AuthenticationException):
    """
    Raised if the registration or update of the user fails.
    """


class InvalidAuthCallException(AuthenticationException):
    """
    Raised if the code started executing unexpected flow.
    """


class InvalidArgumentException(BaseTxmException):
    """
    Raised if invalid argument received.
    """


def require_auth_condition(condition: bool, message: Optional[str] = None):
    """
    Raises InvalidAuthCallException with message if condition is false.
    """
    if not condition:
        raise InvalidAuthCallException(message)
