# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '10/22/15'

import six

from stonemason.pyramid import Hilbert, Legacy

from ..concept import StorageKeyConcept


class HilbertKeyMode(StorageKeyConcept):
    def __call__(self, prefix, index, extension):
        fragments = [prefix]
        fragments.extend(Hilbert.coord2dir(index.z, index.x, index.y))
        fragments.append('%d-%d-%d@%d%s' % (index.z, index.x, index.y,
                                            index.stride, extension))
        return self._sep.join(fragments)


class LegacyKeyMode(StorageKeyConcept):
    def __call__(self, prefix, index, extension):
        fragments = [prefix]
        fragments.extend(Legacy.coord2dir(index.z, index.x, index.y))
        fragments.append('%d-%d-%d@%d%s' % (index.z, index.x, index.y,
                                            index.stride, extension))
        return self._sep.join(fragments)


class SimpleKeyMode(StorageKeyConcept):
    def __call__(self, prefix, index, extension):
        fragments = [prefix]
        fragments.extend([str(index.z), str(index.x), str(index.y)])
        fragments.append('%d-%d-%d@%d%s' % (index.z, index.x, index.y,
                                            index.stride, extension))
        return self._sep.join(fragments)


KEY_MODES = dict(hilbert=HilbertKeyMode,
                 legacy=LegacyKeyMode,
                 simple=SimpleKeyMode, )


def create_key_mode(mode, sep):
    assert isinstance(sep, six.string_types)
    try:
        class_ = KEY_MODES[mode]
    except KeyError:
        raise RuntimeError('Invalid storage key mode "%s"' % mode)
    return class_(sep=sep)
