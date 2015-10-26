# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '10/26/15'

import six

from stonemason.pyramid import MetaTileIndex, Hilbert, Legacy

from ..concept import StorageKeyConcept


# ==============================================================================
# MetaTile Key Mode
# ==============================================================================
class MetaTileKeyConcept(StorageKeyConcept):  # pragma: no cover
    def __init__(self, prefix='', extension='.png', sep='/', gzip=False):
        assert isinstance(prefix, six.string_types)
        assert extension.startswith('.')
        self._prefix = prefix
        self._extension = extension
        self._sep = sep

        if gzip:  # append '.gz' to extension
            self._extension = self._extension + '.gz'


class HilbertKeyMode(MetaTileKeyConcept):
    def __call__(self, index):
        assert isinstance(index, MetaTileIndex)
        z, x, y, stride = index

        fragments = [self._prefix]
        fragments.extend(Hilbert.coord2dir(z, x, y))
        fragments.append('%d-%d-%d@%d%s' % (z, x, y, stride, self._extension))
        return self._sep.join(fragments)


class LegacyKeyMode(MetaTileKeyConcept):
    def __call__(self, index):
        assert isinstance(index, MetaTileIndex)
        z, x, y, stride = index

        fragments = [self._prefix]
        fragments.extend(Legacy.coord2dir(z, x, y))
        fragments.append('%d-%d-%d@%d%s' % (z, x, y, stride, self._extension))
        return self._sep.join(fragments)


class SimpleKeyMode(MetaTileKeyConcept):
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
    try:
        class_ = KEY_MODES[mode]
    except KeyError:
        raise RuntimeError('Invalid storage key mode "%s"' % mode)
    return class_(**kwargs)
