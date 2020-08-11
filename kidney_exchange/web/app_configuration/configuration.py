import logging
import os
from dataclasses import dataclass

from flask import current_app as app

from kidney_exchange.web.app_configuration.context import get_or_set

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Config:
    """
    Configuration of the web application.
    """

    # Postgres configuration
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_url: str


def get_config() -> Config:
    """
    Obtains configuration from the application context.
    """
    return get_or_set('config', build_configuration)


def build_configuration() -> Config:
    """
    Builds configuration from environment or from the Flask properties
    """
    logger.debug('Building configuration.')
    config = Config(
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
