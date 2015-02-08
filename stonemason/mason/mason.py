# -*- encoding: utf-8 -*-
"""
    stonemason.mason.mason
    ~~~~~~~~~~~~~~~~~~~~~~

    Facade StoneMason.

"""

import os
import six

from stonemason.provider.pyramid import Pyramid
from stonemason.provider.tileprovider import TileProviderBuilder

from .theme import JsonThemeParser


class Mason(object):
    """Stonemason Facade"""

    def __init__(self):
        self._providers = dict()

    def load_theme_from_file(self, filepath):
        themes = JsonThemeParser().read_from_file(filepath)

        for theme in themes:
            tag = theme.name
            pyramid = Pyramid(**theme.pyramid._asdict())

            builder = TileProviderBuilder(tag, pyramid)
            builder.build_metadata(**theme.metadata._asdict())
            builder.build_cache(**theme.cache._asdict())
            builder.build_storage(**theme.storage._asdict())

            provider = builder.build()

            self._providers[provider.tag] = provider

    def load_theme_from_directory(self, dirpath):

        for filename in os.listdir(dirpath):

            _, ext = os.path.splitext(filename)
            #TODO: USE NOT ONLY JSON FORMAT
            if ext != '.json':
                continue

            filepath = os.path.join(dirpath, filename)
            self.load_theme_from_file(filepath)

    def load_theme_from_s3(self, s3path):
        raise NotImplemented

    def get_metadata(self, tag):
        provider = self._providers[tag]
        return provider.describe()

    def list_metadata(self):
        return list(p.describe() for p in six.itervalues(self._providers))

    def get_tile(self, tag, z, x, y, scale, ext):
        provider = self._providers[tag]
        tile = provider.get_tile(z, x, y)
        return tile

    def close(self):
        for provider in six.itervalues(self._providers):
            provider.close()
