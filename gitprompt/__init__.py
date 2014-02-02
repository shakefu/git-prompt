"""
Bash Prompt
===========

"""
import argparse

import pyconfig
import blessings

from . import fields


DEBUG = False


def default_prompt(f):
    prompt = "\r{c.cyan}{user}{c.normal}@{host} {time}"

    if f.venv:
        if f.venv and str(f.git.repo).lower() != str(f.venv).lower():
            prompt += " {c.yellow}{venv}{c.normal}"
        else:
            prompt += " {venv}"

    if f.git.repo:
        if f.venv and str(f.git.repo).lower() != str(f.venv).lower():
            prompt += " {c.yellow}{git.repo}{c.normal}"
        else:
            prompt += " {git.repo}"
        prompt += " {git.branch}"
        prompt += " {git.all_changes}"
        prompt += " {git.status}"

    prompt += "\n"
    prompt += "{cwd}"
    return prompt


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



