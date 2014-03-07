import re
import commands

from gitprompt.fields.base import Field


class repo(Field):
    """ Current actual repo name from remote origin if in a git repo. """
    error, text = commands.getstatusoutput(
            "git remote show -n origin | grep Fetch")
    if error:
        value = ''
    else:
        if not text.endswith('.git'):
            # This may happen if there's not a remote set up for the repo
            value = text.split()[-1]
        else:
            value = text.split('/')[-1].split('.git')[0]


class repo_lower(Field):
    """ Current lower case repo name from remote origin if in a git repo. """
    value = repo.value.lower()


class branch(Field):
    """ Current git branch name if in a git repo. """
    error, text = commands.getstatusoutput(
            "git rev-parse --abbrev-ref HEAD")
    value = text if not error else ''


class status(Field):
    """ Current git status in short form if in a git repo. """
    error, text = commands.getstatusoutput("git -c color.ui=always status -s")
    if text:
        value = '\n' + text.rstrip() if not error else ''
    else:
        value = ''


class flake_status(Field):
    """ Current git status with extra information if there are pyflakes
    violations. """
    error, text = commands.getstatusoutput("git -c color.ui=always status -s")
    if error or not text:
        value = ''
    else:
        value = text.split('\n')
        for i in xrange(len(value)):
            line = value[i]
            filename = line.split()[-1]
            if filename.endswith('.py'):
                error, text = commands.getstatusoutput("pyflakes " + filename)
                if error:
                    value[i] = '{c.bold_yellow}!{c.normal}' + value[i]
                else:
                    value[i] = ' ' + value[i]
            else:
                value[i] = ' ' + value[i]

        value = '\n'.join(value)
        # value = '\n' + text.rstrip() if not error else ''


def _lines_committed():
    """ Return a tuple of the number of changed lines in commits. """
    error, text = commands.getstatusoutput(
            "git log --shortstat --branches --since='midnight' "
            "--author $(git config --get user.email)")
    if error:
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


def _lines_uncommitted(staged=False):
    """ Return a tuple of the number of changed lines staged. """
    cmd = "git diff --numstat"
    if staged:
        cmd += " --staged"
    error, text = commands.getstatusoutput(cmd)
    if error:
        return 0, 0
    inserted, deleted = 0, 0
    for line in text.split('\n'):
        if not line: continue
        i, d, _ = line.split()
        try:
            i, d = int(i), int(d)
        except:
            i, d = 0, 0
        inserted += i
        deleted += d

    return inserted, deleted


def _format_lines_changed(inserted, deleted):
    value = ''
    if inserted:
        value += '{c.green}++{c.normal}%s' % inserted
    if deleted:
        value += '{c.red}--{c.normal}%s' % deleted
    return value


class all_changes(Field):
    """ Return all changed lines, commited, staged, and unstaged.

    ++74--32

    """
    value = (_lines_committed(), _lines_uncommitted(),
            _lines_uncommitted(staged=True))
    value = map(lambda a, b, c: a + b + c, *value)
    value = _format_lines_changed(*value)


class committed_changes(Field):
    """ Return commited changed lines.

    ++74--32

    """
    value = _format_lines_changed(*_lines_committed())


def get_fields():
    """
    Return all the fields defined or imported into this module.

    """
    fields = globals().copy()
    for key in fields.keys():
        if key.startswith('_'):
            continue
        if not type(fields[key]) == Field.__metaclass__:
            del fields[key]

    return fields

