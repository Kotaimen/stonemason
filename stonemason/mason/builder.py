# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/10/15'

import re

import six

from stonemason.pyramid import Pyramid
from stonemason.provider.formatbundle import MapType, TileFormat, FormatBundle
from stonemason.provider.tilestorage import NullClusterStorage, \
    DiskClusterStorage, S3ClusterStorage
from stonemason.renderer.tilerenderer import NullMetaTileRenderer, \
    ImageMetaTileRenderer, RendererExprParser

from .theme import Theme, SchemaTheme
from .portrayal import Portrayal
from .metadata import Metadata
from .schema import Schema, HybridSchema
from .exceptions import UnknownStorageType, UnknownRendererType, \
    InvalidSchemaTag


def create_cluster_storage(bundle, pyramid, **config):
    prototype = config.pop('prototype', 'null')
    if prototype == 'null':
        return NullClusterStorage()
    elif prototype == 'disk':
        return DiskClusterStorage(
            levels=pyramid.levels,
            stride=pyramid.stride,
            format=bundle,
            **config)
    elif prototype == 's3':
        return S3ClusterStorage(
            levels=pyramid.levels,
            stride=pyramid.stride,
            format=bundle,
            **config)
    else:
        raise UnknownStorageType(prototype)


def create_metatile_renderer(bundle, pyramid, **config):
    layers = config.get('layers')
    if layers is None:
        return NullMetaTileRenderer()

    prototype = config.pop('prototype', 'null')
    if prototype == 'null':
        return NullMetaTileRenderer()
    elif prototype == 'image':
        renderer = RendererExprParser(pyramid).parse_from_dict(
            layers, 'root').interpret()
        return ImageMetaTileRenderer(pyramid, bundle, renderer)
    else:
        raise UnknownRendererType(prototype)


class SchemaBuilder(object):
    def __init__(self):
        self._tag = None
        self._map_type = MapType('image')
        self._tile_format = TileFormat('PNG')
        self._pyramid = Pyramid()
        self._storage = NullClusterStorage()
        self._renderer = NullMetaTileRenderer()

    def build(self):
        if self._tag is None:
            self._tag = '%s' % self._tile_format.extension

        if re.match('^[0-9].*', self._tag):
            raise InvalidSchemaTag(
                'Tag of TileMatrix should not start with a number')

        matrix = HybridSchema(self._tag, self._storage, self._renderer)
        return matrix

    def build_tag(self, tag):
        assert isinstance(tag, six.string_types)
        self._tag = tag

    def build_pyramid(self, **config):
        self._pyramid = Pyramid(**config)

    def build_map_type(self, t):
        assert isinstance(t, six.string_types)
        self._map_type = MapType(t)

    def build_tile_format(self, **config):
        self._tile_format = TileFormat(**config)

    def build_storage(self, **config):
        bundle = FormatBundle(self._map_type, self._tile_format)

        prototype = config.pop('prototype', 'null')
        if prototype == 'null':
            self._storage = NullClusterStorage()
        elif prototype == 'disk':
            self._storage = DiskClusterStorage(
                levels=self._pyramid.levels,
                stride=self._pyramid.stride,
                format=bundle,
                **config)
        elif prototype == 's3':
            self._storage = S3ClusterStorage(
                levels=self._pyramid.levels,
                stride=self._pyramid.stride,
                format=bundle,
                **config)
        else:
            raise UnknownStorageType(prototype)

    def build_renderer(self, **config):
        bundle = FormatBundle(self._map_type, self._tile_format)

        layers = config.get('layers')
        if layers is None:
            self._renderer = NullMetaTileRenderer()

        prototype = config.pop('prototype', 'null')
        if prototype == 'null':
            self._renderer = NullMetaTileRenderer()
        elif prototype == 'image':
            renderer = RendererExprParser(self._pyramid).parse_from_dict(
                layers, 'root').interpret()
            self._renderer = ImageMetaTileRenderer(self._pyramid, bundle,
                                                   renderer)
        else:
            raise UnknownRendererType(prototype)


class PortrayalBuilder(object):
    def __init__(self):
        self._name = ''
        self._metadata = Metadata()
        self._map_type = MapType('image')
        self._tile_format = TileFormat('PNG')
        self._pyramid = Pyramid()

        self._schemas = dict()

    def build(self):
        return Portrayal(
            name=self._name,
            metadata=self._metadata,
            bundle=FormatBundle(self._map_type, self._tile_format),
            pyramid=self._pyramid,
            schemas=self._schemas
        )

    def build_name(self, name):
        assert isinstance(name, six.string_types)
        self._name = name

    def build_metadata(self, **config):
        self._metadata = Metadata(**config)

    def build_pyramid(self, **config):
        self._pyramid = Pyramid(**config)

    def build_map_type(self, t):
        assert isinstance(t, six.string_types)
        self._map_type = MapType(t)

    def build_tile_format(self, **config):
        self._tile_format = TileFormat(**config)

    def add_schema(self, schema):
        assert isinstance(schema, Schema)
        self._schemas[schema.tag] = schema


def create_portrayal_from_theme(theme):
    assert isinstance(theme, Theme)
    builder = PortrayalBuilder()
    if theme.name is not None:
        builder.build_name(theme.name)
    if theme.metadata is not None:
        builder.build_metadata(**theme.metadata)
    if theme.pyramid is not None:
        builder.build_pyramid(**theme.pyramid)
    if theme.maptype is not None:
        builder.build_map_type(theme.maptype)
    if theme.tileformat is not None:
        builder.build_tile_format(**theme.tileformat)

    for schema_theme in theme.schemas:
        assert isinstance(schema_theme, SchemaTheme)
        schema_builder = SchemaBuilder()

        if schema_theme.tag is not None:
            schema_builder.build_tag(schema_theme.tag)
        if schema_theme.pyramid is not None:
            schema_builder.build_pyramid(**schema_theme.pyramid)
        if schema_theme.maptype is not None:
            schema_builder.build_map_type(schema_theme.maptype)
        if schema_theme.tileformat is not None:
            schema_builder.build_tile_format(**schema_theme.tileformat)
        if schema_theme.storage is not None:
            schema_builder.build_storage(**schema_theme.storage)
        if schema_theme.renderer is not None:
            schema_builder.build_renderer(**schema_theme.renderer)

        matrix = schema_builder.build()

        builder.add_schema(matrix)

    return builder.build()