# -*- encoding: utf-8 -*-
"""
    stonemason.storage.tilestorage.mapper
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Implements metatile key modes.
"""
__author__ = 'ray'
__date__ = '10/26/15'

import six

from stonemason.pyramid import MetaTileIndex, Hilbert, Legacy

from ..concept import StorageKeyConcept


# ==============================================================================
# MetaTile Key Mode
# ==============================================================================
class MetaTileKeyConcept(StorageKeyConcept):  # pragma: no cover
    """MetaTile Key Concept

    Basic class for MetaTile key mode. A MetaTile key mode maps a MetaTile index
    into a literal string.

    :param prefix: Prefix of the key string.
    :type prefix: str

    :param extension: Suffix of the key string.
    :type extension: str

    :param sep: The character used to separate key components.
    :type sep: str

    :param gzip: If append .gz after extension.
    :type gzip: bool

    """

    def __init__(self, prefix='', extension='.png', sep='/', gzip=False):
        assert isinstance(prefix, six.string_types)
        assert extension.startswith('.')
        self._prefix = prefix
        self._extension = extension
        self._sep = sep

        if gzip:  # append '.gz' to extension
            self._extension = self._extension + '.gz'


class HilbertKeyMode(MetaTileKeyConcept):
    """Hilbert key Mode

    The ``HilbertKeyMode`` uses algorithm of hilbert curves to flatten a three
    dimensional index into one in order to keep the storage locality of
    nearby tiles.

    """

    def __call__(self, index):
        assert isinstance(index, MetaTileIndex)
        z, x, y, stride = index

        fragments = [self._prefix]
        fragments.extend(Hilbert.coord2dir(z, x, y))
        fragments.append('%d-%d-%d@%d%s' % (z, x, y, stride, self._extension))
        return self._sep.join(fragments)


class LegacyKeyMode(MetaTileKeyConcept):
    """Legacy Key Mode

    The ``LegacyKeyMode`` maps the index to a string patten that was used in
    the early mason project.

    """

    def __call__(self, index):
        assert isinstance(index, MetaTileIndex)
        z, x, y, stride = index

        fragments = [self._prefix]
        fragments.extend(Legacy.coord2dir(z, x, y))
        fragments.append('%d-%d-%d@%d%s' % (z, x, y, stride, self._extension))
        return self._sep.join(fragments)


class SimpleKeyMode(MetaTileKeyConcept):
    """Simple Key Mode

    The ``SimpleKeyMode`` simply maps z, x, y coordinates and stride of metatile
    index to a '-' separated string.
    """

    def __call__(self, index):
        assert isinstance(index, MetaTileIndex)
        z, x, y, stride = index

        fragments = [self._prefix]
        fragments.extend([str(z), str(x), str(y)])
        fragments.append('%d-%d-%d@%d%s' % (z, x, y, stride, self._extension))
        return self._sep.join(fragments)


KEY_MODES = dict(hilbert=HilbertKeyMode,
                 legacy=LegacyKeyMode,
                 simple=SimpleKeyMode)


def create_key_mode(mode, **kwargs):
    """Factory that create metatile key mode."""
    try:
        class_ = KEY_MODES[mode]
    except KeyError:
        raise RuntimeError('Invalid storage key mode "%s"' % mode)
    return class_(**kwargs)
