import logging
import os

from yoyo import read_migrations, get_backend

logger = logging.getLogger(__name__)


def migrate_db(db_uri: str):
    """
    Runs db migrations.
    :param db_uri
    :return:
    """
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

        # Rollback all migrations - just sample
        # backend.rollback_migrations(backend.to_rollback(migrations))
    logger.info("DB migrations applied.")
