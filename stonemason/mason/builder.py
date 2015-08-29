# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/10/15'

import re
import uuid
from collections import OrderedDict

import six

from stonemason.pyramid import Pyramid
from stonemason.formatbundle import MapType, TileFormat, FormatBundle
from stonemason.renderer import MasonRenderer
from stonemason.tilestorage import NullClusterStorage, ClusterStorage, \
    MetaTileStorage, DiskClusterStorage, S3ClusterStorage, DiskMetaTileStorage, \
    S3MetaTileStorage

from .theme import Theme, SchemaTheme
from .mapbook import MapBook
from .metadata import Metadata
from .mapsheet import MapSheet, ClusterMapSheet, MetaTileMapSheet
from .exceptions import UnknownStorageType, InvalidMapSheetTag


class MapSheetBuilder(object):
    def __init__(self):
        self._tag = ''
        self._map_type = MapType('image')
        self._tile_format = TileFormat('PNG')
        self._pyramid = Pyramid()
        self._storage = NullClusterStorage()
        self._renderer = MasonRenderer({})

    def build(self):
        if re.match('^[0-9].*', self._tag):
            raise InvalidMapSheetTag(
                'Tag of TileMatrix should not start with a number')

        bundle = FormatBundle(self._map_type, self._tile_format)

        if isinstance(self._storage, ClusterStorage):
            map_sheet = ClusterMapSheet(
                self._tag, bundle, self._pyramid, self._storage, self._renderer)
        elif isinstance(self._storage, MetaTileStorage):
            map_sheet = MetaTileMapSheet(
                self._tag, bundle, self._pyramid, self._storage, self._renderer)
        else:
            # Should not reach here
            raise NotImplementedError

        return map_sheet

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
            self._storage = DiskClusterStorage(format=bundle, **config)
        elif prototype == 's3':
            self._storage = S3ClusterStorage(format=bundle, **config)
        elif prototype == 'disk.metatile':
            self._storage = DiskMetaTileStorage(format=bundle, **config)
        elif prototype == 's3.metatile':
            self._storage = S3MetaTileStorage(format=bundle, **config)
        else:
            raise UnknownStorageType(prototype)

    def build_renderer(self, **config):
        expression = config.get('layers')
        if expression is None:
            expression = dict()

        self._renderer = MasonRenderer(expression)


class MapBookBuilder(object):
    def __init__(self):
        self._name = ''
        self._metadata = Metadata()

        self._map_sheets = OrderedDict()

    def build(self):
        return MapBook(
            name=self._name,
            metadata=self._metadata,
            map_sheets=self._map_sheets
        )

    def build_name(self, name):
        assert isinstance(name, six.string_types)
        self._name = name

    def build_metadata(self, **config):
        self._metadata = Metadata(**config)

    def add_map_sheet(self, map_sheet):
        assert isinstance(map_sheet, MapSheet)
        self._map_sheets[map_sheet.tag] = map_sheet


def create_map_book_from_theme(theme):
    assert isinstance(theme, Theme)
    builder = MapBookBuilder()
    if theme.name is not None:
        builder.build_name(theme.name)
    if theme.metadata is not None:
        builder.build_metadata(**theme.metadata)

    for sheet_theme in theme.schemas:
        assert isinstance(sheet_theme, SchemaTheme)
        map_sheet_builder = MapSheetBuilder()

        sheet_tag = 'tag-%s' % uuid.uuid4().hex
        if sheet_theme.tag is not None:
            sheet_tag = sheet_theme.tag
        map_sheet_builder.build_tag(sheet_tag)

        if sheet_theme.pyramid is not None:
            map_sheet_builder.build_pyramid(**sheet_theme.pyramid)

        if sheet_theme.maptype is not None:
            map_sheet_builder.build_map_type(sheet_theme.maptype)

        if sheet_theme.tileformat is not None:
            map_sheet_builder.build_tile_format(**sheet_theme.tileformat)

        if sheet_theme.storage is not None:
            map_sheet_builder.build_storage(**sheet_theme.storage)

        if sheet_theme.renderer is not None:
            map_sheet_builder.build_renderer(**sheet_theme.renderer)

        map_sheet = map_sheet_builder.build()

        builder.add_map_sheet(map_sheet)

    return builder.build()
