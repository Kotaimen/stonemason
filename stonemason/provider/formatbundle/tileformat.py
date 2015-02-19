# -*- encoding: utf-8 -*-

"""
    stonemason.provider.formatbundle.tileformat
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tile formats
"""
__author__ = 'kotaimen'
__date__ = '2/19/15'

import collections

import six

from stonemason.util.guesstypes import guess_extension
from .exceptions import InvalidTileFormat

_TileFormat = collections.namedtuple('_TileFormat',
                                     'format extension mimetype parameters')


class TileFormat(_TileFormat):
    """Type of map

    """
    __slots__ = ()

    # TODO: Allow register custom formats
    KNOWN_FORMATS = {
        'JPEG': 'image/jpeg',
        'PNG': 'image/png',
    }

    def __new__(cls, format=None, extension=None,
                mimetype=None, parameter=None):

        if format is not None and mimetype is None:
            if format not in cls.KNOWN_FORMATS:
                raise InvalidTileFormat(format)

        if mimetype is None:
            mimetype = cls.KNOWN_FORMATS[format]

        if extension is None:
            extension = guess_extension(mimetype)

        if parameter is None:
            parameter = dict()

        assert isinstance(mimetype, six.string_types)
        assert isinstance(extension, six.string_types)
        assert isinstance(parameter, dict)

        return _TileFormat.__new__(cls, format, extension, mimetype, parameter)
