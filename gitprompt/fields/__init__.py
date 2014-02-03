"""
Prompt Fields
=============

"""
import os
import pwd
import datetime
import platform

from gitprompt.fields import git
from gitprompt.fields.base import Field


class user(Field):
    """ Current username. """
    value = pwd.getpwuid(os.getuid())[0]


class host(Field):
    """ Current hostname. """
    value = platform.node()


class venv(Field):
    """ Current virtualenv name if it exists. """
    value = os.path.basename(os.environ.get("VIRTUAL_ENV", ''))


class cwd(Field):
    """ Current directory, last two path members. """
    value = os.getcwd()
    value = value.split('/')[-2:]
    value = os.path.join(*value)


class time(Field):
    """ Current time in 12-hour format. """
    value = datetime.datetime.now().strftime("%I:%M:%S")


class time_24(Field):
    """ Current time in 24-hour format. """
    value = datetime.datetime.now().strftime("%X")


class time_utc(Field):
    """ Current UTC time in 24-hour format. """
    value = datetime.datetime.utcnow().strftime("%X")


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
