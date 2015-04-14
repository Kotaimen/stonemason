# -*- encoding: utf-8 -*-

"""
    stonemason.cli.context
    ~~~~~~~~~~~~~~~~~~~~~~

    Shared Click context definition.
"""

__author__ = 'kotaimen'
__date__ = '3/2/15'

import click

CONTEXT_SETTINGS = dict(
    auto_envvar_prefix='STONEMASON',  # Click adds "_" automatically
    help_option_names=['-h', '--help'],
)


class Context(object):
    """Custom context object, collecting options from group command,
    and pass them to sub commands."""

    def __init__(self):
        self.gallery = None
        self.verbose = 0
        self.debug = 0


# Context passes into subcommands
pass_context = click.make_pass_decorator(Context)

