# -*- coding: latin-1 -*-
"""
Bash Prompt
===========

"""
import os
import argparse

import pyconfig
import blessings

from gitprompt import fields


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


def jakes_prompt(f):
    console_width = int(os.environ.get('COLUMNS'))
    decor = 10
    term = blessings.Terminal(force_styling=True)
    no_color = blessings.Terminal(force_styling=None)

    # Top line
    padding = " " * (console_width - decor)

    if f.venv and f.venv != f.git.repo:
        repo_color = venv_color = "{c.red}"
    else:
        repo_color = "{c.cyan}"
        venv_color = "{c.magenta}"

    # Venv
    width = 18
    padding = padding[width - 1:]
    if f.venv:
        venv = "═" * (width - len(" (" + str(f.venv) + ") "))
        venv = "{c.blue}" + venv + "{c.normal}"
        venv = (" {c.yellow}(" + venv_color + "{venv}{c.yellow}){c.normal} "
                + venv)
    else:
        venv = "{c.blue}═{c.normal}" * width

    # Repo/Branch
    width = 30
    padding = padding[width:]
    if f.git.repo:
        git = ' %s/%s ' % (f.git.repo, f.git.branch) + '== '
        git = "═" * (width - len(git))
        git = "{c.blue}" + git + "{c.normal}"
        git = (git + " " + repo_color
                + "{git.repo}{c.yellow}/{c.normal}{git.branch} ")
        if f.git.all_changes:
            git += "{c.blue}══{c.normal} "
        else:
            git += "{c.blue}═══{c.normal}"
    else:
        git = "{c.blue}═{c.normal}" * width

    # Changes
    width = 12
    padding = padding[width:]
    if f.git.all_changes:
        changes = str(f.git.all_changes).format(c=no_color) + " "
        changes = "═" * (width - len(changes))
        changes = str(f.git.all_changes) + " {c.blue}" + changes + "{c.normal}"
    else:
        changes = "{c.blue}═{c.normal}" * width

    # User@Host
    padding = padding[len('%s@%s' % (f.user, f.host)):]
    login = "{c.cyan}{user}{c.yellow}@{c.normal}{host}"

    padding = "═" * (len(padding) - 1) + " "
    middle = venv + git + changes + "{c.blue}" + padding + "{c.normal}" + login
    prompt =  "\r {c.blue}╒══{c.normal}" + middle + " {c.blue}══──{c.normal}\n"

    # Git status
    padding = " " * (console_width - decor)

    if f.git.status:
        git_offset = 0
        status = str(f.git.status)
        for line in status.split('\n'):
            if not line.strip():
                continue
            prompt += " {c.blue}│{c.normal}" + " " * git_offset + line + "\n"

    # Bottom line
    padding = " " * (console_width - decor)

    # Current directory
    cwd = str(f.cwd)
    while len(cwd) > len(padding):
        cwd = os.path.join(*cwd.split('/')[1:])
    padding = padding[len(cwd + " ==--"):]
    if cwd != '/':
        cwd = cwd.split('/')
        base = os.path.join(*cwd[:-2]).replace('/', '{c.yellow}/{c.bold_black}')
        cwd = os.path.join(*cwd[-2:]).replace('/', '{c.yellow}/{c.white}')
        cwd = '{c.yellow}/{c.bold_black}' + os.path.join(base, cwd)
        cwd = cwd + '{c.normal}'
    else:
        cwd = '{c.red}/{c.normal}'
    cwd += " {c.blue}══──{c.normal}"

    timestamp = str(f.time)
    padding = padding[len("--== " + timestamp):]
    timestamp = timestamp.replace(':', '{c.yellow}:{c.bold_black}')
    timestamp = '{c.bold_black}' + timestamp + '{c.normal}'

    middle = cwd + padding + "{c.blue}──══ {c.normal}" + timestamp
    prompt += " {c.blue}╘══{c.normal} " + middle + " {c.blue}══──{c.normal}"

    return prompt


pyconfig.set('gitprompt.prompt', jakes_prompt)


def get_prompt(args):
    """ Return a prompt ready to be formatted. """
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


def main():
    # Handle command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug',
            help="enable debug output",
            action='store_true')
    args = parser.parse_args()

    # Get our color helper - thanks blessings
    term = blessings.Terminal(force_styling=True)

    # Get our prompt and make sure it's a string
    prompt = get_prompt(args)

    # Only do this extra check if we're not in debug mode, so a bad prompt will
    # raise up an informative exception
    if not args.debug:
        if not isinstance(prompt, basestring):
            return ''

    # Format our prompt, woot!
    try:
        prompt = prompt.format(c=term, **fields.get_fields())
        prompt = prompt.format(c=term)
    except:
        if args.debug:
            raise
        prompt = ''

    print prompt



