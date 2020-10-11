import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
from txmatching.configuration.app_configuration.application_configuration import build_db_connection_string
from txmatching.database.base import Base

config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None
target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

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
        _get_env_var('POSTGRES_DB')
    )


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=_get_db_connection_string(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    url_key = "sqlalchemy.url"
    configuration = config.get_section(config.config_ini_section)
    if configuration.get(url_key) is None:
        configuration[url_key] = _get_db_connection_string()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=target_metadata.schema,
            include_schemas=True
        )

        with context.begin_transaction():
            context.execute('SET search_path TO public')
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


def _create_db_connection_string_from_parts(
        db_username: str,
        db_password: str,
        db_connection: str,
        db_name: str
) -> str:
    """
    Created DB connection string from parts.
    :param db_username: DB username
    :param db_password: DB password
    :param db_connection:  DB connection
    :param db_name: DB name
    :return: DB connection string
    """
    return f"postgresql://{db_username}:{db_password}@" \
           f"{db_connection}/{_normalize_db_name(db_name)}"

def _normalize_db_name(client: str) -> str:
    """
    Normalize name of the client to the db name.
    :param client: client name
    :return: Database name - basically, lowercase of the client name.

    >>> normalize_db_name('AaBa')
    'aaba'
    """
    return client.lower()
