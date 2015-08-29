# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/2/15'

from flask import make_response

import stonemason
import sys
import platform

VERSION_STRING = '''stonemason:%s

Python: %s

Platform: %s''' % (stonemason.__version__,
         sys.version,
         platform.version())

del stonemason, sys, platform

def health_check():
    """Return a dummy response"""
    response = make_response(VERSION_STRING)
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Cache-Control'] = 'public, max-age=0'

    return response

