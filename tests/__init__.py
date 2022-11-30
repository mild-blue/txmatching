import logging
import os


def try_disable_logging_while_testing(env_variable: str, default_level=logging.NOTSET):
    level = os.getenv(env_variable)
    if level is None:
        level = default_level
    logging.warning(f'All logs with level {level} and lower will be disabled while testing.')
    try:
        logging.disable(level=level)
    except ValueError:
        raise ValueError(f'Unknown level: "{level}". Control .env file.')


try_disable_logging_while_testing(env_variable='LOGGING_DISABLE_LEVEL_FOR_TESTING')
