#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""Main CLI entry point."""

__author__ = 'kotaimen'
__date__ = '2/3/15'

import os
import sys

if sys.argv[0].endswith('__main__.py'):
    # HACK: Fix import error when using Flask reloading
    sys.path.insert(0, os.path.abspath(
        os.path.join(__file__, os.path.pardir, os.path.pardir)))

# Import cli commands
from stonemason.cli import cli

if __name__ == '__main__':
    cli()

