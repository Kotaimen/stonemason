# -*- encoding: utf-8 -*-

"""
    stonemason.formatbundle.tileformat
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
                                     'format mimetype extension parameters')


class TileFormat(_TileFormat):
    """Defines `format` of a map `tile`, and how it is serialised.

    Map data is always a typed object, like :class:`PIL.Image.Image`, then
    serialize into a :class:`bytes` string, then stores as tile data, according
    to :class:`~stonemason.formatbundle.TileFormat` specified in
    :class:`~stonemason.formatbundle.FormatBundle`.

    >>> from stonemason.formatbundle import TileFormat
    >>> format = TileFormat('JPEG', parameters={'quality': 80})
    >>> format.format
    'JPEG'
    >>> format.mimetype
    'image/jpeg'
    >>> format.extension
    '.jpg'
    >>> format.parameters
    {'quality': 80}
    >>> format = TileFormat('JPEG', extension='.jpeg')
    >>> format.extension
    '.jpeg'

    :param format: Format of the tile, supported built-in values are:

        ``JPEG``
            JPEG image

        ``PNG``
            PNG image

        ``TIFF``
            TIFF image

        ``WBP``
            WEBP image, note


        If custom formats are used, `extension` and `mimetype` must also be
        specified.
    :type format: str

    :param extension: File extension of the tile format, default is ``None``,
        which means guess from given `format`.
    :type extension: str

    :param mimetype: Mimetype of the tile format, default is ``None``,
        which means guess from given `format`.
    :type mimetype: str

    :param parameters: Optional format parameters as a dictionary, the actual
        meaning of parameters depends on :class:`~stonemason.formatbundle.MapType`
        and :class:`~stonemason.formatbundle.MapWriter` used.
    :type parameters: dict
    """
    __slots__ = ()

    # TODO: Allow register custom formats
    KNOWN_FORMATS = {
        'JPEG': 'image/jpeg',
        'PNG': 'image/png',
        'TIFF': 'image/tiff',
        'WEBP': 'image/webp',
    }

    def __new__(cls, format=None, extension=None, mimetype=None,
                parameters=None):
        if format is not None and mimetype is None:
            if format not in cls.KNOWN_FORMATS:
                raise InvalidTileFormat(format)

        if mimetype is None:
            mimetype = cls.KNOWN_FORMATS[format]

        if extension is None:
            extension = guess_extension(mimetype)

        if parameters is None:
            parameters = dict()

        assert isinstance(mimetype, six.string_types)
        assert isinstance(extension, six.string_types)
        assert isinstance(parameters, dict)

        return _TileFormat.__new__(cls, format, mimetype, extension, parameters)

    def __repr__(self):
        return 'TileFormat(%s|%s|%s)' % (
            self.format, self.mimetype, self.extension)
