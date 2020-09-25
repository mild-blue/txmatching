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
