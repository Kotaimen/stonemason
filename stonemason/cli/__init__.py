# -*- encoding: utf-8 -*-

"""
    stonemason.cli
    ~~~~~~~~~~~~~~

    Implements stonemason command line interface tool.
"""

__author__ = 'kotaimen'
__date__ = '3/2/15'

from stonemason.pyramid.geo import HAS_GDAL

# import all available commands here
from .main import cli

from .commands.tileserver import tile_server_command
from .commands.check import check_command
from .commands.init import init_theme_root_command

if HAS_GDAL:
    from .commands.tilerenderer import tile_renderer_command
