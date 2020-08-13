import logging
import os
from dataclasses import dataclass

from flask import current_app as app

from kidney_exchange.web.app_configuration.context import get_or_set

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ApplicationConfiguration:
    """
    Configuration of the web application.
    """

    # Postgres configuration
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_url: str


def get_application_configuration() -> ApplicationConfiguration:
    """
    Obtains configuration from the application context.
    """
    return get_or_set('application_configuration', build_application_configuration)


def build_application_configuration() -> ApplicationConfiguration:
    """
    Builds configuration from environment or from the Flask properties
    """
    logger.debug('Building configuration.')
    config = ApplicationConfiguration(
        postgres_user=get_prop('POSTGRES_USER'),
        postgres_password=get_prop('POSTGRES_PASSWORD'),
        postgres_db=get_prop('POSTGRES_DB'),
        postgres_url=get_prop('POSTGRES_URL')
    )
    return config


def get_prop(name: str, optional: bool = False) -> str:
    """
    Gets property from environment or from the flask env.
    """
    config = os.environ.get(name, app.config.get(name))
    if not optional and not config:
        logger.error(f'It was not possible to retrieve configuration for property "{name}"!')
        raise EnvironmentError(f'No existing configuration for "{name}" found!')
    return config
