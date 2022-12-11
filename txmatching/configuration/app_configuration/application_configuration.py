import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from flask import current_app as app

logger = logging.getLogger(__name__)

_DEFAULT_VERSION = 'development'


class ApplicationEnvironment(str, Enum):
    """
    Enum representing the environment the code was build for.
    """
    PRODUCTION = 'PRODUCTION'
    STAGING = 'STAGING'
    DEVELOPMENT = 'DEVELOPMENT'


class ApplicationColourScheme(str, Enum):
    """
    Enum representing the colour scheme to use.
    """
    IKEM = 'IKEM'
    MILD_BLUE = 'MILD_BLUE'


class ApplicationHLAParsing(str, Enum):
    """
    Enum representing the strictness of HLA parsing.
    """
    STRICT = 'STRICT'
    FORGIVING = 'FORGIVING'


@dataclass(frozen=True)
class ApplicationConfiguration:
    """
    Configuration of the web application.
    """
    # pylint: disable=too-many-instance-attributes
    # because this is configuration, we need a lot of attributes

    code_version: str
    environment: ApplicationEnvironment
    hla_parsing: ApplicationHLAParsing
    colour_scheme: ApplicationColourScheme
    # Postgres configuration
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_url: str

    jwt_secret: str
    jwt_expiration_days: int

    # configuration of the SMS service
    use_2fa: bool
    sms_service_url: Optional[str]
    sms_service_sender: Optional[str]
    sms_service_login: Optional[str]
    sms_service_password: Optional[str]
    sentry_dsn: Optional[str]

    # Authentic configuration
    authentic_client_id: str
    authentic_client_secret: str
    authentic_client_redirect_uri: str


def get_application_configuration() -> ApplicationConfiguration:
    """
    Obtains configuration from the application context.
    """
    placeholder = 'APPLICATION_CONFIGURATION'
    if not app.config.get(placeholder):
        app.config[placeholder] = _build_application_configuration()
    return app.config[placeholder]


def _build_application_configuration() -> ApplicationConfiguration:
    """
    Builds configuration from environment or from the Flask properties
    """
    logger.debug('Building configuration.')
    environment = ApplicationEnvironment(_get_prop('ENVIRONMENT'))
    hla_parsing = ApplicationHLAParsing(_get_prop('HLA_PARSING'))
    colour_scheme = ApplicationColourScheme(_get_prop('COLOUR_SCHEME'))
    use_2fa = _get_prop('USE_2FA', default='true').lower() in {'true', 't'}
    code_version = _get_version()

    config = ApplicationConfiguration(
        code_version=code_version,
        environment=environment,
        hla_parsing=hla_parsing,
        colour_scheme=colour_scheme,
        postgres_user=_get_prop('POSTGRES_USER'),
        postgres_password=_get_prop('POSTGRES_PASSWORD'),
        postgres_db=_get_prop('POSTGRES_DB'),
        postgres_url=_get_prop('POSTGRES_URL'),
        jwt_secret=_get_prop('JWT_SECRET'),
        jwt_expiration_days=int(_get_prop('JWT_EXPIRATION_DAYS')),
        use_2fa=use_2fa,
        sms_service_url=_get_prop('SMS_SERVICE_URL', optional=not use_2fa),
        sms_service_sender=_get_prop('SMS_SERVICE_SENDER', optional=not use_2fa),
        sms_service_login=_get_prop('SMS_SERVICE_LOGIN', optional=not use_2fa),
        sms_service_password=_get_prop('SMS_SERVICE_PASSWORD', optional=not use_2fa),
        sentry_dsn=_get_prop('SENTRY_DSN', optional=True),
        authentic_client_id=_get_prop('AUTHENTIC_CLIENT_ID'),
        authentic_client_secret=_get_prop('AUTHENTIC_CLIENT_SECRET'),
        authentic_client_redirect_uri=_get_prop('AUTHENTIC_REDIRECT_URI'),
    )
    return config


def build_db_connection_string(
        postgres_user: str,
        postgres_password: str,
        postgres_url: str,
        postgres_db: str,
        with_psycopg2: bool = True
) -> str:
    prefix = 'postgresql+psycopg2' if with_psycopg2 else 'postgresql'
    return f'{prefix}://{postgres_user}:{postgres_password}@{postgres_url}/{postgres_db}'


def _get_version() -> str:
    """
    Retrieves version from the flask app.

    Returns version of the code and boolean whether the code runs in the production.
    """
    version = _read_version(_DEFAULT_VERSION)
    return version


def _read_version(default: str) -> str:
    """
    Reads version from the file or returns default version.
    """
    file_path = _get_prop('RELEASE_FILE_PATH', optional=True)
    logger.debug(f'File path: {file_path}')

    version = None
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as file:
            version = file.readline().strip()
            logger.debug(f'Setting version as: {version}')

    return version if version else default


def _get_prop(name: str, optional: bool = False, default: str = '') -> str:
    """
    Gets property from environment or from the flask env.
    """
    config = os.environ.get(name, app.config.get(name))
    if not optional and not config:
        logger.error(f'It was not possible to retrieve configuration for property "{name}"!')
        raise EnvironmentError(f'No existing configuration for "{name}" found!')
    return str(config) if config is not None else default
