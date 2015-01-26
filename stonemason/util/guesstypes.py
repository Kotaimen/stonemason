# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '1/25/15'

"""
    stonemason.util.guesstypes
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    Guess mimetypes or file extensions.
"""

import mimetypes

DEFAULT_TYPE = 'application/data'

# mimetypes we cares about...
IMPORTANT_TYPES = [
    ('.dat', 'application/data'),
    ('.txt', 'text/plain'),
    ('.json', 'application/json'),
    ('.jpg', 'image/jpg'),
    ('.jpg', 'image/jpeg'),
    ('.tif', 'image/tiff'),
    ('.tiff', 'image/tiff'),
    ('.png', 'image/png'),
    ('.gif', 'image/gif'),
    ('.webp', 'image/webp'),  # non-official but Google uses this
    ('.wkt', 'application/x-wkt'),
]

EXT2TYPE = dict((k, v) for (k, v) in IMPORTANT_TYPES)
TYPE2EXT = dict((v, k) for (k, v) in reversed(IMPORTANT_TYPES))


def guess_extension(mimetype):
    """Guess extension from mimetype, return empty string on failure.

    Python's standard library ``mimetypes`` is not consistent between python
    versions and operation systems, eg::

        $ python -c 'import mimetypes; print(mimetypes.guess_extension("image/tiff"))'
        .tif
        $ python3 -c 'import mimetypes; print(mimetypes.guess_extension("image/tiff"))'
        .tiff

    :param mimetype: Mimetype to guess.
    :returns: Guessed mimetype, or ``''`` if failed.
    :rtype: str

    """
    if mimetype is None:
        return ''

    try:
        ext = TYPE2EXT[mimetype]
    except KeyError:
        ext = mimetypes.guess_extension(mimetype)
        if ext is None:
            ext = ''
    return ext


def guess_mimetype(extension):
    """Guess mimetype from extension, return ``application/data`` on failure.

    :param mimetype: Extension to guess.
    :returns: Guessed extension, or ``''`` if failed.
    :rtype: str
    """

    if not extension:  # null string or None
        return DEFAULT_TYPE

    try:
        mimetype = TYPE2EXT[extension]
    except KeyError:
        mimetype, encoding = mimetypes.guess_type('foo' + extension)
        if mimetype is None:
            mimetype = DEFAULT_TYPE
        return mimetype
