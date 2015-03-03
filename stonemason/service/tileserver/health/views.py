# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/2/15'

from flask import make_response


def health_check():
    """Return a dummy response"""
    response = make_response()
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

