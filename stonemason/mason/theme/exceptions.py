# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme.exceptions
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A collection of theme exceptions.

"""

__author__ = 'ray'
__date__ = '4/2/15'


class ThemeError(Exception):
    """Basic Theme Error"""
    pass


class ThemeConfigNotFound(ThemeError):
    """Theme Not Found"""
    pass


class InvalidThemeConfig(ThemeError):
    """Invalid Theme Format"""
    pass





