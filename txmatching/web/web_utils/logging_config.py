import json
import logging
import os
from datetime import datetime, timezone
from enum import Enum
from logging.config import dictConfig
from pathlib import Path

from flask import has_request_context, request

logging.getLogger('werkzeug').setLevel('WARNING')  # switch off unnecessary logs from werkzeug

old_factory = logging.getLogRecordFactory()

PATH_TO_LOG = os.getenv('LOGS_FOLDER') or '../logs'


def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    record.request_id = request.request_id if has_request_context() else '-'
    record.remote_addr = request.remote_addr if has_request_context() else '-'
    record.method = request.method if has_request_context() else '-'
    record.path = request.path if has_request_context() else '-'
    return record


logging.setLogRecordFactory(factory=record_factory)


class JsonFormatter(logging.Formatter):

    @staticmethod
    def __prepare_log_data(record):
        data = {
            'datetime': datetime.fromtimestamp(record.created, timezone.utc).strftime(
                '%Y-%m-%dT%H:%M:%S.%fZ'),
            'levelname': record.levelname,
            'name': record.name,
            'process': record.process,
            'user': record.remote_addr,
            'request_id': str(record.request_id),
            'method': record.method,
            'path': record.path,
            'message': record.msg,
        }
        return data

    @staticmethod
    def __insert_exception(record, data):
        if not record.exc_info:
            return
        exception = {
            'stacktrace': str(traceback.format_exception(record.exc_info[0],
                                                         record.exc_info[1],
                                                         record.exc_info[2]))
        }
        # TODO: sometimes json dumps fails for some reason... ??
        # TODO: in order to keep logging alive, we must do this weird catch ??
        json.dumps(exception)
        data['exception'] = exception

    def format(self, record: logging.LogRecord) -> str:
        data = self.__prepare_log_data(record)
        return json.dumps(data)


class ANSIEscapeColorCodes(str, Enum):
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    GREEN = '\033[92m'
    PURPLE = '\033[95m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    END = '\033[0m'


# pylint: disable=too-few-public-methods
class LoggerMaxInfoFilter(logging.Filter):
    """
    Logger filter, which allows logs only with level INFO or lower.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= logging.INFO


# pylint: disable=too-few-public-methods
class LoggerColorfulTerminalOutputFilter(logging.Filter):
    # TODO: fix: colors i files
    """
    Logger filter, which colors logs level name and message to a specific color according to logs level.
    """
    # pylint: disable=too-many-arguments
    def __init__(self,
                 debug_color=None,
                 info_color=None,
                 warning_color=None,
                 error_color=None,
                 critical_color=None):
        super().__init__()
        self.debug_color = debug_color
        self.info_color = info_color or self.debug_color
        self.warning_color = warning_color or self.info_color
        self.error_color = error_color or self.warning_color
        self.critical_color = critical_color or self.error_color
        self.end_color = ANSIEscapeColorCodes.END
        self.levelno_color = {
            logging.DEBUG: self.debug_color,
            logging.INFO: self.info_color,
            logging.WARNING: self.warning_color,
            logging.ERROR: self.error_color,
            logging.CRITICAL: self.critical_color
        }

    def filter(self, record: logging.LogRecord) -> bool:
        color_for_record = self.levelno_color[record.levelno]
        if color_for_record is not None:
            record.levelname = color_for_record + record.levelname + self.end_color
            record.msg = color_for_record + record.msg + self.end_color
        return True


def is_env_variable_value_true(env_variable_value: str, default_env_variable_value: str = 'true') -> bool:
    """
    :param env_variable_value: value from env_variable as string "true"/"false" or None
    :param default_env_variable_value: value if env_variable_value is None
    :return: True if value is "true", False if value is "false", otherwise raises ValueError
    """
    env_variable_value = env_variable_value or default_env_variable_value
    if env_variable_value == 'true':
        return True
    elif env_variable_value == 'false':
        return False
    raise ValueError(f'Invalid .env variable "{env_variable_value}".')


def _get_datetime_format_for_logger():
    return '' if is_env_variable_value_true(os.getenv('DEACTIVATE_DATETIME_IN_LOGGER'),
                                            default_env_variable_value='false') \
              else '%(asctime)s-'


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'max_info_filter': {
            '()': LoggerMaxInfoFilter,
        },
        'colorful_terminal_output': {
            '()': LoggerColorfulTerminalOutputFilter,
            'debug_color': None,
            'info_color': None,
            'warning_color': ANSIEscapeColorCodes.YELLOW if is_env_variable_value_true(os.getenv(
                'COLORFUL_ERROR_OUTPUT')) else None,
            'error_color': ANSIEscapeColorCodes.RED if is_env_variable_value_true(os.getenv(
                'COLORFUL_ERROR_OUTPUT')) else None,
            'critical_color': None
        }
    },
    'loggers': {
        '': {  # root logger
            'level': 'NOTSET',
            'handlers': ['debug_console_handler',
                         'debug_error_console_handler',
                         'info_rotating_file_handler',
                         'error_file_handler'],
        },
        'txmatching': {
            'level': 'NOTSET',
            'handlers': ['debug_console_handler',
                         'debug_error_console_handler',
                         'info_rotating_file_handler',
                         'error_file_handler'],
            'propagate': False
        }
    },
    'handlers': {
        'debug_console_handler': {
            'level': 'NOTSET',
            'filters': ['max_info_filter'],
            'formatter': 'json' if is_env_variable_value_true(os.getenv('PRODUCTION_LOGGER')) else 'info',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'debug_error_console_handler': {
            'level': 'WARNING',
            'filters': ['colorful_terminal_output'],
            'formatter': 'json' if is_env_variable_value_true(os.getenv('PRODUCTION_LOGGER')) else 'error',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },
        'info_rotating_file_handler': {
            'level': 'INFO',
            'formatter': 'info',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': f'{PATH_TO_LOG}/info.log',
            'mode': 'a',
            'maxBytes': 1048576,
            'backupCount': 10
        },
        'error_file_handler': {
            'level': 'WARNING',
            'formatter': 'error',
            'class': 'logging.FileHandler',
            'filename': f'{PATH_TO_LOG}/error.log',
            'mode': 'a',
        },
        # Just a sample of email logger, not used now
        'critical_mail_handler': {
            'level': 'CRITICAL',
            'formatter': 'error',
            'class': 'logging.handlers.SMTPHandler',
            'mailhost': 'localhost',
            'fromaddr': 'error.handler@mild.blue',
            'toaddrs': ['marek.polak@mild.blue'],
            'subject': 'Critical error with application TXMatching.'
        }
    },
    'formatters': {
        'info': {
            'format': f'{_get_datetime_format_for_logger()}'
                      f'%(levelname)s-%(name)s::%(module)s|%(lineno)s:: %(message)s'
        },
        'error': {
            'format': f'{_get_datetime_format_for_logger()}'
                      f'%(levelname)s-%(name)s-%(process)d::%(module)s|%(lineno)s:: %(message)s'
        },
        'json': {
            '()': JsonFormatter
        }
    },
}


def setup_logging():
    if not is_env_variable_value_true(os.getenv('LOGGER_DEBUG')):
        # logger debug mode is inactive
        logging.disable(logging.DEBUG)
    # Prepare logging folder if it does not exist
    Path(PATH_TO_LOG).mkdir(parents=True, exist_ok=True)
    dictConfig(LOGGING_CONFIG)
