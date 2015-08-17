# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '8/11/15'

import logging
import importlib
import subprocess

logger = logging.getLogger(__name__)


def has_module(name):
    try:
        importlib.import_module(name)
    except ImportError:
        logger.debug('Module %s not found' % name)
        return False
    else:
        logger.debug('Module %s found' % name)
        return True


def has_executable(name, *args):
    try:
        subprocess.check_output([name] + list(args))
    except subprocess.CalledProcessError:
        logger.debug('Executable %s not found' % name)
        return False
    else:
        logger.debug('Executable %s found' % name)
        return True


HAS_MAPNIK = has_module('mapnik')

HAS_GDAL = has_module('osgeo.gdal')

HAS_SCIPY = has_module('scipy')

HAS_SKIMAGE = has_module('skimage')

HAS_IMAGEMAGICK = has_executable('convert', '-version')
