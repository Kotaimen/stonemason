# -*- encoding: utf-8 -*-
"""
    stonemason.renderer.cartographer.inspect
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Utilities for inspecting modules and executable in current environment.
"""
__author__ = 'ray'
__date__ = '8/11/15'

import logging
import importlib
import subprocess

logger = logging.getLogger(__name__)


def has_module(name):
    """Check if module `name` exists.

    :param name: name of the module to check.
    :type name: str

    :return: true if module exists.
    :rtype: bool
    """
    try:
        importlib.import_module(name)
    except ImportError:
        logger.debug('Module %s not found' % name)
        return False
    else:
        logger.debug('Module %s found' % name)
        return True


def has_executable(name, *args):
    """Check if executable `name` exists.

    :param name: name of the executable to check.
    :type name: str

    :return: true if module exists.
    :rtype: bool
    """
    try:
        subprocess.check_output([name] + list(args))
    except subprocess.CalledProcessError:
        logger.debug('Executable %s not found' % name)
        return False
    else:
        logger.debug('Executable %s found' % name)
        return True


#: The flag that shows if mapnik module exists
HAS_MAPNIK = has_module('mapnik')

#: The flag that shows if GDAL module exists
HAS_GDAL = has_module('osgeo.gdal')

#: The flag that shows if scipy module exists
HAS_SCIPY = has_module('scipy')

#: The flag that shows if skimage module exists
HAS_SKIMAGE = has_module('skimage')

#: The flag that shows if imagemagick executable exists
HAS_IMAGEMAGICK = has_executable('convert', '-version')
