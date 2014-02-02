import re
import commands

from .base import Field


class branch(Field):
    """ Current git branch name if in a git repo. """
    def value(cls):
        status, text = commands.getstatusoutput(
                "git rev-parse --abbrev-ref HEAD")
        return text if not status else ''


class status(Field):
    """ Current git status in short form if in a git repo.

     M gitprompt/__init__.py
    M  setup.py
    ?? gitprompt/field.py

    """
    def value(cls):
        status, text = commands.getstatusoutput(
                "git -c color.ui=always status -s")
        return text if not status else ''


class all_changed(Field):
    """ Return all changed lines, commited, staged, and unstaged.

    ++74--32

    """
    def value(cls):
        inserted, deleted = _lines_committed()

        out = ''
        if inserted:
            out += '{c.green}++{c.normal}%s' % inserted
        if deleted:
            out += '{c.red}--{c.normal}%s' % deleted
        return out


def _lines_committed():
    """ Return a tuple of the number of changed lines in commits. """
    status, text = commands.getstatusoutput(
            "git log --shortstat --branches --since='midnight' "
            "--author $(git config --get user.email)")
    if status:
        return 0, 0

    inserted_count = 0
    deleted_count = 0
    for line in text.split('\n'):
        if not re.match('\s*\d+ files? change', line):
            continue
        line = line.split(',')[1:]
        for field in line:
            inserted = re.search('(\d+) insertion', field)
            if inserted:
                inserted_count += int(inserted.group(1))

            deleted = re.search('(\d+) deletion', field)
            if deleted:
                deleted_count += int(deleted.group(1))

    return inserted_count, deleted_count


def _lines_staged():
    """ Return a tuple of the number of changed lines staged. """


def _lines_unstaged():
    """ Return a tuple of the number of changed lines that're unstaged. """


def get_fields():
    """
    Return all the fields defined or imported into this module.

    """
    fields = globals().copy()
    for key in fields.keys():
        if not type(fields[key]) == Field.__metaclass__:
            del fields[key]

    return fields

