import logging
import os
import re
from dataclasses import dataclass
from typing import Tuple, Optional

from flask import current_app as app

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ApplicationConfiguration:
    """
    Configuration of the web application.
    """
    # pylint: disable=too-many-instance-attributes
    # because this is configuration, we need a lot of attributes

    code_version: str
    is_production: bool
    # Postgres configuration
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_url: str

    jwt_secret: str
    jwt_expiration_days: int

    # configuration of the SMS service
    # required only when running in the production
    sms_service_url: Optional[str]
    sms_service_sender: Optional[str]
    sms_service_login: Optional[str]
    sms_service_password: Optional[str]


def get_application_configuration() -> ApplicationConfiguration:
    """
    Obtains configuration from the application context.
    """
    place_holder = 'APPLICATION_CONFIGURATION'
    if not app.config.get(place_holder):
        app.config[place_holder] = _build_application_configuration()
    return app.config[place_holder]


def _build_application_configuration() -> ApplicationConfiguration:
    """
    Builds configuration from environment or from the Flask properties
    """
    logger.debug('Building configuration.')
    code_version, is_production = _get_version()

    config = ApplicationConfiguration(
        code_version=code_version,
        is_production=is_production,
        postgres_user=_get_prop('POSTGRES_USER'),
        postgres_password=_get_prop('POSTGRES_PASSWORD'),
        postgres_db=_get_prop('POSTGRES_DB'),
        postgres_url=_get_prop('POSTGRES_URL'),
        jwt_secret=_get_prop('JWT_SECRET'),
        jwt_expiration_days=int(_get_prop('JWT_EXPIRATION_DAYS')),
        sms_service_url=_get_prop('SMS_SERVICE_URL', optional=not is_production),
        sms_service_sender=_get_prop('SMS_SERVICE_SENDER', optional=not is_production),
        sms_service_login=_get_prop('SMS_SERVICE_LOGIN', optional=not is_production),
        sms_service_password=_get_prop('SMS_SERVICE_PASSWORD', optional=not is_production)
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


def _get_prop(name: str, optional: bool = False) -> str:
    """
    Gets property from environment or from the flask env.
    """
    config = os.environ.get(name, app.config.get(name))
    if not optional and not config:
        logger.error(f'It was not possible to retrieve configuration for property "{name}"!')
        raise EnvironmentError(f'No existing configuration for "{name}" found!')
    return str(config) if config is not None else ''


def _get_version() -> Tuple[str, bool]:
    """
    Retrieves version from the flask app.

    Returns version of the code and boolean whether the code runs in the production.
    """
    version = _read_version('development')
    return version, _determine_is_production_from_version(version)


def _determine_is_production_from_version(version: str) -> bool:
    """
    Returns true if the current version uses semantic versioning.
    The semantic versioning indicates that the code is tagged, thus released.
    >>> _determine_is_production_from_version('1.2.3')
    True
    >>> _determine_is_production_from_version('10.20.30')
    True
    >>> _determine_is_production_from_version('10.20.30-dirty')
    False
    >>> _determine_is_production_from_version('development')
    False
    """
    return bool(re.match(r'^\d+\.\d+\.\d+$', version))


def _read_version(default: str) -> str:
    """
    Reads version from the file or returns default version.
    """
    file_path = os.environ.get('RELEASE_FILE_PATH')
    file_path = file_path if file_path else app.config.get('RELEASE_FILE_PATH')
    logger.debug(f'File path: {file_path}')

    version = None
    if file_path:
        with open(file_path, 'r') as file:
            version = file.readline().strip()
            logger.debug(f'Setting version as: {version}')

    return version if version else default
