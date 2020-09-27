from typing import Optional


class AuthenticationException(Exception):
    """
    Base class for Authentication related exceptions.
    """


class InvalidJWTException(AuthenticationException):
    """
    Exception indicating that JWT was for some reason invalid.
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
    Raised if the registration or user update fails.
    """


class InvalidAuthCallException(AuthenticationException):
    """
    Raised if the code started executing unexpected flow.
    """


def require_auth_condition(condition: bool, message: Optional[str] = None):
    """
    If condition is false, raises InvalidAuthCallException with message.
    """
    if not condition:
        raise InvalidAuthCallException(message)
