# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/8/15'

import json

from .theme import MetadataConfig, PyramidConfig, CacheConfig, StorageConfig
from .theme import Theme


class ThemeParser(object):
    CONFIG_TAG_NAME = 'name'

    CONFIG_TAG_METADATA = 'metadata'

    CONFIG_TAG_PYRAMID = 'pyramid'

    CONFIG_TAG_CACHE = 'cache'

    CONFIG_TAG_STORAGE = 'storage'

    def read_from_file(self, filename):
        raise NotImplementedError


class JsonThemeParser(ThemeParser):
    def read_from_file(self, filename):
        with open(filename, 'r') as fp:
            config = json.loads(fp.read())

        name = config.get(self.CONFIG_TAG_NAME)

        config_metadata = MetadataConfig(
            **config.get(self.CONFIG_TAG_METADATA, dict()))

        config_pyramid = PyramidConfig(
            **config.get(self.CONFIG_TAG_PYRAMID, dict()))

        config_cache = CacheConfig(
            **config.get(self.CONFIG_TAG_CACHE, dict()))

        config_storage = StorageConfig(
            **config.get(self.CONFIG_TAG_STORAGE, dict()))

        return [Theme(name=name,
                      metadata=config_metadata,
                      pyramid=config_pyramid,
                      cache=config_cache,
                      storage=config_storage)]
