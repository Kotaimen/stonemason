# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '2/19/15'


class FormatError(Exception):
    pass


class InvalidMapType(FormatError):
    pass


class InvalidTileFormat(FormatError):
    pass


class NoMatchingMapWriter(FormatError):
    pass
