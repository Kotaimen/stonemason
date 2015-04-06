# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/28/15'


class MasonError(Exception):
    pass


class MapNotFound(MasonError):
    pass


class DuplicatedMap(MasonError):
    pass


class MapBuildError(MasonError):
    pass

