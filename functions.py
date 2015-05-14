# Do not remove these Imports. They enable log and dbg when importing * from functions
import lib.log as log
import logging
from lib.log import dbg

import re
from datetime import datetime

__author__ = 'tehsphinx'


def to_camelcase(s):
    return re.sub(r'(?!^)_([a-zA-Z])', lambda m: m.group(1).upper(), s.capitalize())


def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

