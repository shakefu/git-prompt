# -*- coding: latin-1 -*-
"""
Bash Prompt
===========

"""
import os
import argparse

import pyconfig
import blessings

DEBUG = False


def default_prompt(f):
    prompt = "\r{c.cyan}{user}{c.normal}@{host} {time}"

    if f.venv:
        if f.venv and f.git.repo != f.venv:
            prompt += " {c.yellow}{venv}{c.normal}"
        else:
            prompt += " {venv}"

    if f.git.repo:
        if f.venv and f.git.repo != f.venv:
            prompt += " {c.yellow}{git.repo}{c.normal}"
        else:
            prompt += " {git.repo}"
        prompt += " {git.branch}"
        prompt += " {git.all_changes}"
        prompt += " {git.status}"

    prompt += "\n"
    prompt += "{cwd}"
    return prompt


def shakefus_prompt(f):
    console_width = int(os.environ.get('COLUMNS'))
    decor = 10
    # term = blessings.Terminal(force_styling=True)
    no_color = blessings.Terminal(force_styling=None)

    # Top line
    padding = " " * (console_width - decor)

    if f.venv and f.venv != f.git.repo:
        repo_color = venv_color = "{c.red}"
    else:
        repo_color = "{c.cyan}"
        venv_color = "{c.magenta}"

    # Venv
    width = 12
    if f.venv:
        length = len(" (" + str(f.venv) + ") ")
        if length > width:
            width = length + 1
        venv = "═" * (width - length)
        venv = "{line_color}" + venv + "{c.normal}"
        venv = (" {c.yellow}(" + venv_color + "{venv}{c.yellow}){c.normal} "
                + venv)
    else:
        venv = "{line_color}═{c.normal}" * width
    padding = padding[width - 1:]

    # Repo/Branch
    width = 20
    if f.git.repo:
        git = ' %s/%s ' % (f.git.repo, f.git.branch) + '== '
        length = len(git)
        if length > width:
            width = length + 1
        git = "═" * (width - length)
        git = "{line_color}" + git + "{c.normal}"
        git = (git + " " + repo_color
                + "{git.repo}{c.yellow}/{c.normal}{git.branch} ")
        if f.git.all_changes:
            git += "{line_color}══{c.normal} "
        else:
            git += "{line_color}═══{c.normal}"
    else:
        git = "{line_color}═{c.normal}" * width
    padding = padding[width:]

    # Changes
    width = 16
    padding = padding[width:]
    if f.git.all_changes:
        changes = str(f.git.all_changes).format(c=no_color) + " "
        changes = "═" * (width - len(changes))
        changes = str(f.git.all_changes) + " {line_color}" + changes + "{c.normal}"
    else:
        changes = "{line_color}═{c.normal}" * width

    # User@Host
    padding = padding[len('%s@%s' % (f.user, f.host)):]
    login = "{c.cyan}{user}{c.yellow}@{c.normal}{host}"

    padding = "═" * (len(padding) - 1) + " "
    middle = venv + git + changes + "{line_color}" + padding + "{c.normal}" + login
    prompt =  "\r {line_color}╒══{c.normal}" + middle + " {line_color}══──{c.normal}\n"

    # Git status
    padding = " " * (console_width - decor)

    '''
    if f.git.status:
        git_offset = 0
        status = str(f.git.status)
        for line in status.split('\n'):
            if not line.strip():
                continue
            prompt += " {line_color}│{c.normal}" + " " * git_offset + line + "\n"
    '''
    if f.git.flake_status:
        git_offset = 0
        status = str(f.git.flake_status)
        for line in status.split('\n'):
            if not line.strip():
                continue
            prompt += " {line_color}│{c.normal}" + " " * git_offset + line + "\n"

    # Bottom line
    padding = " " * (console_width - decor)

    # Current directory
    cwd = str(f.cwd)
    while len(cwd) > len(padding):
        cwd = os.path.join(*cwd.split('/')[1:])
    padding = padding[len(cwd + " ==--"):]
    if cwd != '/':
        cwd = cwd.split('/')
        if len(cwd) > 2:
            base = os.path.join(*cwd[:-2]).replace('/', '{c.yellow}/{c.bold_black}')
            cwd = os.path.join(*cwd[-2:]).replace('/', '{c.yellow}/{c.white}')
        else:
            base = ''
            cwd = os.path.join(*cwd[-2:]).replace('/', '{c.yellow}/{c.white}')
        cwd = '{c.yellow}/{c.bold_black}' + os.path.join(base, cwd)
        cwd = cwd + '{c.normal}'
    else:
        cwd = '{c.red}/{c.normal}'
    cwd += " {line_color}══──{c.normal}"

    timestamp = str(f.time)
    padding = padding[len("--== " + timestamp):]
    timestamp = timestamp.replace(':', '{c.yellow}:{c.bold_black}')
    timestamp = '{c.bold_black}' + timestamp + '{c.normal}'

    middle = cwd + padding + "{line_color}──══ {c.normal}" + timestamp
    prompt += " {line_color}╘══{c.normal} " + middle + " {line_color}══──{c.normal}"

    return prompt


def get_prompt(args):
    """ Return a prompt ready to be formatted. """
    # Late import 'cause this actually does a bunch of work, and we want to
    # catch exceptions that happen in its loading, further up the call stack
    from gitprompt import fields

    # Allow overriding with pyconfig
    prompt = pyconfig.get('gitprompt.prompt', default_prompt)

    # If the fetched prompt is a callable, we call it with the fields module to
    # create the new prompt format string
    if callable(prompt):
        try:
            return prompt(fields)
        except:
            if args.debug:
                raise
            return ''
    elif prompt:
        return prompt


def _get_args():
    """ Return parsed command line arguments. """
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug',
            help="enable debug output",
            action='store_true')
    return parser.parse_args()


def main():
    try:
        # Get the args
        args = _get_args()
    except:
        print ''
        return

    try:
        # Get our color helper - thanks blessings
        term = blessings.Terminal(force_styling=True)
        # Get our prompt and make sure it's a string
        prompt = get_prompt(args)

        # Only do this extra check if we're not in debug mode, so a bad prompt will
        # raise up an informative exception
        if not args.debug:
            if not isinstance(prompt, basestring):
                return ''
    except:
        if args.debug:
            raise
        prompt = ''

    # Format our prompt, woot!
    try:
        # Late import 'cause this actually does a bunch of work, and we want to
        # catch exceptions that happen in its loading
        from gitprompt import fields

        format_context = pyconfig.get('gitprompt.custom_context', {})
        format_context.update(fields.get_fields())
        format_context.setdefault('line_color', term.color(105))
        format_context.setdefault('c', term)

        prompt = prompt.format(**format_context)
        # This isn't a dupe, we format twice, since fields can have colors
        prompt = prompt.format(**format_context)
    except:
        if args.debug:
            raise
        prompt = ''

    print prompt



