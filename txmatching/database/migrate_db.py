import logging
import os
from typing import Optional

from yoyo import get_backend, read_migrations

from txmatching.configuration.app_configuration.application_configuration import \
    build_db_connection_string

logger = logging.getLogger(__name__)


def _get_env_var(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f'Environment variable "{name}" not set up, can not run migrations.')
    return value


def _get_db_connection_string() -> str:
    """
    Get connection string from profile.
    :return: Connection string to Postgres.
    """
    return build_db_connection_string(
        _get_env_var('POSTGRES_USER'),
        _get_env_var('POSTGRES_PASSWORD'),
        _get_env_var('POSTGRES_URL'),
        _get_env_var('POSTGRES_DB'),
        False
    )


def migrate_db(db_uri: Optional[str] = None):
    """
    Runs db migrations.
    :param db_uri
    :return:
    """
    if not db_uri:
        db_uri = _get_db_connection_string()
    acceptable_db_uri = db_uri.replace('+psycopg2', '')
    backend = get_backend(acceptable_db_uri)
    directory = os.path.dirname(os.path.realpath(__file__))
    migration_directory = os.path.join(directory, 'db_migrations')
    logger.info(f'Applying DB migrations from {migration_directory}.')
    migrations = read_migrations(migration_directory)

    logger.info('Applying DB migrations:')
    for migration in migrations:
        logger.info(migration.id)

    with backend.lock():
        # Apply any outstanding migrations
        backend.apply_migrations(backend.to_apply(migrations))
    logger.info('DB migrations applied.')


if __name__ == '__main__':
    migrate_db()
