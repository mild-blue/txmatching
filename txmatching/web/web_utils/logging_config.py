import logging
import os
from logging.config import dictConfig
from pathlib import Path

logging.getLogger('werkzeug').setLevel('WARNING')  # switch off unnecessary logs from werkzeug

PATH_TO_LOG = '../logs'


class LoggerJustInfoFilter(logging.Filter):

    def filter(self, record) -> bool:
        return record.levelno == logging.INFO


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'just_info_filter': {
            '()': LoggerJustInfoFilter,
        }
    },
    'loggers': {
        '': {  # root logger
            'level': 'NOTSET',
            'handlers': ['debug_console_handler', 'debug_error_console_handler', 'info_rotating_file_handler', 'error_file_handler'],
        },
        'txmatching': {
            'level': 'NOTSET',
            'handlers': ['debug_console_handler', 'debug_error_console_handler', 'info_rotating_file_handler', 'error_file_handler'],
            'propagate': False
        }
    },
    'handlers': {
        'debug_console_handler': {
            'level': 'INFO',
            'filters': ['just_info_filter'],
            'formatter': 'info',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'debug_error_console_handler': {
            'level': 'WARNING',
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
            'format': f'{"" if os.getenv("DEACTIVATE_DATETIME_IN_LOGGER") == "true" else "%(asctime)s-"}'
                      '%(levelname)s-%(name)s::%(module)s|%(lineno)s:: %(message)s'
        },
        'error': {
            'format': f'{"" if os.getenv("DEACTIVATE_DATETIME_IN_LOGGER") == "true" else "%(asctime)s-"}'
                      f'%(levelname)s-%(name)s-%(process)d::%(module)s|%(lineno)s:: %(message)s'
        },
    },
}


def setup_logging():
    # Prepare logging folder if it does not exist
    Path(PATH_TO_LOG).mkdir(parents=True, exist_ok=True)
    dictConfig(LOGGING_CONFIG)
