# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/28/15'

from stonemason.pyramid import Pyramid
from stonemason.provider.tilestorage import NullClusterStorage, \
    DiskClusterStorage, S3ClusterStorage
from stonemason.provider.formatbundle import MapType, TileFormat, FormatBundle
from stonemason.provider.tileprovider import StorageTileProvider, \
    RendererTileProvider, HybridTileProvider, NullTileProvider
from stonemason.renderer.tilerenderer import \
    NullMetaTileRenderer, ImageMetaTileRenderer, RendererExprParser

from .theme import Theme
from .masonmap import MasonMap
from .exceptions import MapBuildError


CLUSTER_STORAGES = {
    'null': NullClusterStorage,
    'disk': DiskClusterStorage,
    's3': S3ClusterStorage
}


def make_cluster_storage(prototype, bundle, pyramid, **parameters):
    if prototype == 'null':
        return NullClusterStorage()

    setup = CLUSTER_STORAGES.get(prototype)
    if setup is None:
        raise MapBuildError('Unknown storage type: "%s"' % prototype)

    return setup(levels=pyramid.levels, stride=pyramid.stride,
                 format=bundle, **parameters)


def make_metatile_renderer(prototype, bundle, pyramid, **parameters):
    layers = parameters.get('layers')
    if layers is None:
        return NullMetaTileRenderer()

    if prototype == 'image':
        renderer = RendererExprParser(pyramid).parse_from_dict(
            layers, 'root').interpret()
        return ImageMetaTileRenderer(pyramid, bundle, renderer)
    elif prototype == 'null':
        return NullMetaTileRenderer()
    else:
        raise MapBuildError('Unknown renderer type: "%s"' % prototype)


class MapBuilder(object):
    PROVIDER_MODE = ['storage', 'renderer', 'hybrid', 'null']

    def build_from_theme(self, theme, mode='storage'):
        assert isinstance(theme, Theme)
        assert mode in self.PROVIDER_MODE

        name = theme.name
        maptype = MapType(theme.maptype)
        metadata = theme.metadata.attributes
        pyramid = Pyramid(**theme.pyramid.attributes)

        if mode == 'null':
            provider = NullTileProvider()
            return MasonMap(name, metadata, provider)
        elif mode == 'storage':
            tileformat = TileFormat(**theme.storage.tileformat)
            bundle = FormatBundle(maptype, tileformat)

            storage = make_cluster_storage(
                prototype=theme.storage.prototype,
                bundle=bundle,
                pyramid=pyramid,
                **theme.storage.parameters
            )
            provider = StorageTileProvider(maptype, pyramid, storage)

            return MasonMap(name, metadata, provider)
        elif mode == 'renderer':
            tileformat = TileFormat(**theme.design.tileformat)
            bundle = FormatBundle(maptype, tileformat)

            renderer = make_metatile_renderer(
                prototype=maptype.type,
                bundle=bundle,
                pyramid=pyramid,
                **theme.design.attributes
            )
            provider = RendererTileProvider(maptype, pyramid, bundle, renderer)

            return MasonMap(name, metadata, provider)
        elif mode == 'hybrid':
            tileformat = TileFormat(**theme.design.tileformat)
            bundle = FormatBundle(maptype, tileformat)

            storage = make_cluster_storage(
                prototype=theme.storage.prototype,
                bundle=bundle,
                pyramid=pyramid,
                **theme.storage.parameters
            )
            storage_provider = StorageTileProvider(maptype, pyramid, storage)

            renderer = make_metatile_renderer(
                prototype=maptype.type,
                bundle=bundle,
                pyramid=pyramid,
                **theme.design.attributes
            )
            renderer_provider = RendererTileProvider(
                maptype, pyramid, bundle, renderer)

            provider = HybridTileProvider(storage_provider, renderer_provider)

            return MasonMap(name, metadata, provider)

        else:
            raise MapBuildError('Unknown provider mode "%s"' % mode)
