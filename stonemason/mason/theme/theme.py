# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/8/15'

from collections import namedtuple


class ThemeError(Exception):
    pass


_MetadataConfig = namedtuple('MetadataConfig', 'attribution')


class MetadataConfig(_MetadataConfig):
    __slots__ = ()

    def __new__(cls, attribution='K&R'):
        return _MetadataConfig.__new__(cls, attribution)


_PyramidConfig = namedtuple('PyramidConfig',
                            'levels stride crs proj boundary')


class PyramidConfig(_PyramidConfig):
    __slots__ = ()

    def __new__(cls, levels=range(0, 23),
                stride=1,
                crs='EPSG:4326',
                proj='EPSG:3857',
                boundary=(-180, -85.0511, 180, 85.0511)):
        return _PyramidConfig.__new__(
            cls, levels=levels, stride=stride,
            crs=crs, proj=proj, boundary=boundary)


_CacheConfig = namedtuple('__CacheConfig', 'prototype parameters')


class CacheConfig(_CacheConfig):
    __slots__ = ()

    def __new__(cls, prototype='null', parameters=None):
        if parameters is None:
            parameters = dict()
        return _CacheConfig.__new__(
            cls, prototype=prototype, parameters=parameters)


_StorageConfig = namedtuple('StorageConfig', 'prototype parameters')


class StorageConfig(_StorageConfig):
    __slots__ = ()

    def __new__(cls, prototype='null', parameters=None):
        if parameters is None:
            parameters = dict()
        return _StorageConfig.__new__(
            cls, prototype=prototype, parameters=parameters)


_Theme = namedtuple('Theme', 'name metadata pyramid cache storage')


class Theme(_Theme):
    __slots__ = ()

    def __new__(cls,
                name=None,
                metadata=None,
                pyramid=None,
                cache=None,
                storage=None):

        if name is None:
            raise ThemeError('A Theme must have a Name!')

        if metadata is None:
            metadata = MetadataConfig()

        if pyramid is None:
            pyramid = PyramidConfig()

        if cache is None:
            cache = CacheConfig()

        if storage is None:
            storage = StorageConfig()

        return _Theme.__new__(
            cls,
            name=name,
            metadata=metadata,
            pyramid=pyramid,
            cache=cache,
            storage=storage
        )
