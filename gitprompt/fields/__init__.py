"""
Prompt Fields
=============

"""
import os
import pwd
import datetime
import platform

from . import git
from .base import Field


class user(Field):
    """ Current username. """
    def value(cls):
        return pwd.getpwuid(os.getuid())[0]


class host(Field):
    """ Current hostname. """
    def value(cls):
        return platform.node()


class venv(Field):
    """ Current virtualenv name if it exists. """
    def value(cls):
        return os.path.basename(os.environ.get("VIRTUAL_ENV", ''))


class cwd(Field):
    """ Current directory, last two path members. """
    value = os.getcwd()
    value = value.split('/')[-2:]
    value = os.path.join(*value)


def get_fields():
    """
    Return all the fields defined or imported into this module.

    """
    submodules = ['git']
    fields = globals().copy()
    for key in fields.keys():
        if key in submodules:
            continue
        if not type(fields[key]) == Field.__metaclass__:
            del fields[key]

    return fields
