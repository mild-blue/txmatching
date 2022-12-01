import logging
import os
from enum import Enum
from logging.config import dictConfig
from pathlib import Path

logging.getLogger('werkzeug').setLevel('WARNING')  # switch off unnecessary logs from werkzeug

PATH_TO_LOG = '../logs'


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

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= logging.INFO


# pylint: disable=too-few-public-methods
class LoggerColorfulTerminalOutputFilter(logging.Filter):

    # pylint: disable=too-many-arguments
    def __init__(self,
                 debug_color=None,
                 info_color=None,
                 warning_color=None,
                 error_color=None,
                 critical_color=None):
        super().__init__()
        self.debug_color = debug_color
        self.info_color = info_color if info_color is not None else self.debug_color
        self.warning_color = warning_color if warning_color is not None else self.info_color
        self.error_color = error_color if error_color is not None else self.warning_color
        self.critical_color = critical_color if critical_color is not None else self.error_color
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


def is_var_active_in_env(env_variable_value: str, default_env_variable_value: str = 'true') -> bool:
    env_variable_value = default_env_variable_value if env_variable_value is None else env_variable_value
    if env_variable_value == 'true':
        return True
    elif env_variable_value == 'false':
        return False
    raise ValueError(f'Invalid .env variable "{env_variable_value}".')


def _get_datetime_format_for_logger():
    return '' if is_var_active_in_env(os.getenv('DEACTIVATE_DATETIME_IN_LOGGER'),
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
            'warning_color': ANSIEscapeColorCodes.YELLOW if is_var_active_in_env(os.getenv(
                'COLORFUL_ERROR_OUTPUT')) else None,
            'error_color': ANSIEscapeColorCodes.RED if is_var_active_in_env(os.getenv(
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
            'formatter': 'info',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'debug_error_console_handler': {
            'level': 'WARNING',
            'filters': ['colorful_terminal_output'],
            'formatter': 'error',
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
    },
}


def setup_logging():
    if not is_var_active_in_env(os.getenv('LOGGER_DEBUG')):
        # logger debug mode is inactive
        logging.disable(logging.DEBUG)
    # Prepare logging folder if it does not exist
    Path(PATH_TO_LOG).mkdir(parents=True, exist_ok=True)
    dictConfig(LOGGING_CONFIG)
