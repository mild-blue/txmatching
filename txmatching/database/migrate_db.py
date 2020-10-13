import os

from yoyo import read_migrations, get_backend

from txmatching.configuration.app_configuration.application_configuration import build_db_connection_string


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

backend = get_backend(_get_db_connection_string())
directory = os.path.dirname(os.path.realpath(__file__))
migration_directory = os.path.join(directory, 'db_migrations')
print(f'Applying DB migrations from {migration_directory}.')
migrations = read_migrations(migration_directory)

print('Applying DB migrations:')
for migration in migrations:
    print(migration.id)

with backend.lock():
    # Apply any outstanding migrations
    backend.apply_migrations(backend.to_apply(migrations))

    # Rollback all migrations - just sample
    # backend.rollback_migrations(backend.to_rollback(migrations))
print("DB migrations applied.")
