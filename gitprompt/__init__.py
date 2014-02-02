"""
Bash Prompt
===========

"""
import pyconfig
import blessings

from . import fields
# Preload so available as attribute on fields
from .fields import git


def get_prompt():
    """ Return a prompt ready to be formatted. """
    # Allow overriding with pyconfig
    prompt = pyconfig.get('gitprompt.prompt')
    if callable(prompt):
        return prompt(fields)
    elif prompt:
        return prompt

    prompt = "\r{c.yellow}{user}{c.normal}@{host}"
    if fields.venv:
        prompt += " {venv}"
    if fields.git.branch:
        prompt += " {git.branch}"
        prompt += " {git.all_changed}"
        prompt += "\n{git.status}"
    prompt += "\n{cwd}"
    prompt += "\n"
    return prompt


def main():
    term = blessings.Terminal(force_styling=True)
    prompt = get_prompt().format(c=term, **fields.get_fields())
    prompt = prompt.format(c=term)
    print prompt



