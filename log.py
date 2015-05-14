from datetime import datetime
from threading import current_thread
import logging

__author__ = 'tehsphinx'

DEBUG_STR = 'debug'
INFO_STR = 'info'
WARNING_STR = 'warning'
ERROR_STR = 'error'
CRITICAL_STR = 'critical'

LOG_LEVEL = logging.WARNING
logging.basicConfig(level=LOG_LEVEL, format='')


def dbg(*args, log_level=None, **kwargs):
    if not log_level:
        log_level = DEBUG_STR

    if logging.getLogger().getEffectiveLevel() != LOG_LEVEL:
        logging.getLogger().setLevel(LOG_LEVEL)

    msg = _format_dbg_msg(*args, **kwargs)
    getattr(logging, log_level)(msg)


def debug(*args, **kwargs):
    dbg(*args, log_level=DEBUG_STR, **kwargs)


def info(*args, **kwargs):
    dbg(*args, log_level=INFO_STR, **kwargs)


def warn(*args, **kwargs):
    dbg(*args, log_level=WARNING_STR, **kwargs)


def warning(*args, **kwargs):
    dbg(*args, log_level=WARNING_STR, **kwargs)


def error(*args, **kwargs):
    dbg(*args, log_level=ERROR_STR, **kwargs)


def critical(*args, **kwargs):
    dbg(*args, log_level=CRITICAL_STR, **kwargs)


def _format_dbg_msg(*args, **kwargs):
    return '{datetime} {thread} -- {args} {kwargs}'.format(
        datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        thread=current_thread().getName(),
        args=' '.join([str(x) for x in args]),
        kwargs=' '.join(['{key}={val}'.format(key=k, val=str(v)) for k, v in kwargs.items()])
    )
