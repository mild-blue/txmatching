import json
import logging
import os
import traceback
from copy import copy
from datetime import datetime, timezone
from enum import Enum
from logging.config import dictConfig
from pathlib import Path

from flask import has_request_context, request

logging.getLogger('werkzeug').setLevel('WARNING')  # switch off unnecessary logs from werkzeug

PATH_TO_LOG = os.getenv('LOGS_FOLDER') or '../logs'

old_factory = logging.getLogRecordFactory()


def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    record.request_id = request.request_id if has_request_context() and hasattr(request, 'request_id') else '-'
    record.remote_addr = request.remote_addr if has_request_context() and hasattr(request, 'remote_addr') else '-'
    record.method = request.method if has_request_context() and hasattr(request, 'method') else '-'
    record.path = request.path if has_request_context() and hasattr(request, 'path') else '-'
    return record


logging.setLogRecordFactory(factory=record_factory)


class ANSIEscapeColorCodes(str, Enum):
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    GREEN = '\033[92m'
    PURPLE = '\033[95m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    END = '\033[0m'


class BaseFormatter(logging.Formatter):
    # pylint: disable=too-many-arguments
    def __init__(self,
                 is_colorful_output=False,
                 debug_color=ANSIEscapeColorCodes.END,
                 info_color=ANSIEscapeColorCodes.END,
                 warning_color=ANSIEscapeColorCodes.END,
                 error_color=ANSIEscapeColorCodes.END,
                 critical_color=ANSIEscapeColorCodes.END):
        super().__init__()
        self.is_colorful_output = is_colorful_output
        self.levelno_color = {
            logging.DEBUG: debug_color,
            logging.INFO: info_color,
            logging.WARNING: warning_color,
            logging.ERROR: error_color,
            logging.CRITICAL: critical_color
        }

    @staticmethod
    def __color_string(string: str, color: str) -> str:
        return color + string + ANSIEscapeColorCodes.END

    def format(self, record: logging.LogRecord) -> str:
        time = datetime.fromtimestamp(record.created,
                                      timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        tmp_levelname = copy(record.levelname)
        tmp_msg = copy(record.msg)
        if self.is_colorful_output:
            tmp_levelname = self.__color_string(string=tmp_levelname,
                                                color=self.levelno_color[record.levelno])
            tmp_msg = self.__color_string(string=tmp_msg,
                                          color=self.levelno_color[record.levelno])
        return f'{time}-{tmp_levelname}-{record.name}-{record.process}:: ' \
               f'{record.module}|{record.lineno}:: {tmp_msg}'


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
        try:
            json.dumps(exception)
            data['exception'] = exception
        except TypeError as ex:
            logger = logging.getLogger('JsonLogFormatter')
            logger.error(f'Json dumps failed with {ex} for original exception {exception}. '
                         f'Original record: {record}.')

    def format(self, record: logging.LogRecord) -> str:
        data = self.__prepare_log_data(record)
        self.__insert_exception(record, data)
        return json.dumps(data)


# pylint: disable=too-few-public-methods
class LoggerMaxInfoFilter(logging.Filter):
    """
    Logger filter, which allows logs only with level INFO or lower.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= logging.INFO


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


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'max_info_filter': {
            '()': LoggerMaxInfoFilter,
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
            'formatter': 'json' if is_env_variable_value_true(os.getenv('PRODUCTION_LOGGER')) else 'terminal_info',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'debug_error_console_handler': {
            'level': 'WARNING',
            'formatter': 'json' if is_env_variable_value_true(os.getenv('PRODUCTION_LOGGER')) else 'terminal_error',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },
        'info_rotating_file_handler': {
            'level': 'INFO',
            'formatter': 'file_info',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': f'{PATH_TO_LOG}/info.log',
            'mode': 'a',
            'maxBytes': 1048576,
            'backupCount': 10
        },
        'error_file_handler': {
            'level': 'WARNING',
            'formatter': 'file_error',
            'class': 'logging.FileHandler',
            'filename': f'{PATH_TO_LOG}/error.log',
            'mode': 'a',
        },
        # Just a sample of email logger, not used now
        'critical_mail_handler': {
            'level': 'CRITICAL',
            'formatter': 'file_error',
            'class': 'logging.handlers.SMTPHandler',
            'mailhost': 'localhost',
            'fromaddr': 'error.handler@mild.blue',
            'toaddrs': ['marek.polak@mild.blue'],
            'subject': 'Critical error with application TXMatching.'
        }
    },
    'formatters': {
        'terminal_info': {
            '()': BaseFormatter,
        },
        'terminal_error': {
            '()': BaseFormatter,
            'is_colorful_output': is_env_variable_value_true(os.getenv('COLORFUL_ERROR_OUTPUT')),
            'warning_color': ANSIEscapeColorCodes.YELLOW,
            'error_color': ANSIEscapeColorCodes.RED,
            'critical_color': ANSIEscapeColorCodes.RED
        },
        'file_info': {
            '()': BaseFormatter,
            'is_colorful_output': False
        },
        'file_error': {
            '()': BaseFormatter,
            'is_colorful_output': False
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
