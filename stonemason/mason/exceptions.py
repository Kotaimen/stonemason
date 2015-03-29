# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/28/15'


class MasonError(Exception):
    pass


class MapBuildError(MasonError):
    pass


class DuplicatedMapError(MasonError):
    pass


