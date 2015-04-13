# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/10/15'


class MasonError(Exception):
    pass


class UnknownStorageType(MasonError):
    pass


class UnknownRendererType(MasonError):
    pass
