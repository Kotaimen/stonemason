# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/28/15'

from stonemason.pyramid import Pyramid
from stonemason.provider.tilestorage import NullClusterStorage, \
    DiskClusterStorage, S3ClusterStorage
from stonemason.provider.formatbundle import MapType, TileFormat, FormatBundle
from stonemason.provider.tileprovider import HybridTileProvider
from stonemason.renderer.tilerenderer import \
    NullMetaTileRenderer, ImageMetaTileRenderer, RendererExprParser

from .theme import MapTheme
from .masonmap import MasonMap, Metadata
from .exceptions import MapBuildError


CLUSTER_STORAGES = {
    'disk': DiskClusterStorage,
    's3': S3ClusterStorage
}


def make_cluster_storage(bundle, pyramid, **parameters):
    prototype = parameters.get('prototype')
    if prototype is None or prototype == 'null':
        return NullClusterStorage()

    setup = CLUSTER_STORAGES.get(prototype)
    if setup is None:
        raise MapBuildError('Unknown storage type: "%s"' % prototype)

    parameters = dict(parameters)
    parameters.pop('prototype')

    return setup(levels=pyramid.levels, stride=pyramid.stride,
                 format=bundle, **parameters)


def make_metatile_renderer(bundle, pyramid, **parameters):
    prototype = parameters.get('prototype')
    if prototype is None or prototype == 'null':
        return NullMetaTileRenderer()

    layers = parameters.get('layers')
    if layers is None:
        return NullMetaTileRenderer()

    if prototype == 'image':
        renderer = RendererExprParser(pyramid).parse_from_dict(
            layers, 'root').interpret()
        return ImageMetaTileRenderer(pyramid, bundle, renderer)
    else:
        raise MapBuildError('Unknown renderer type: "%s"' % prototype)


class MapBuilder(object):
    def build_from_theme(self, theme):
        assert isinstance(theme, MapTheme)

        # get theme name
        name = theme.name

        # build map metadata
        metadata = Metadata(**theme.metadata)

        # build pyramid
        pyramid = Pyramid(**theme.pyramid)

        # build format bundle
        maptype = MapType(theme.maptype)
        tileformat = TileFormat(**theme.tileformat)
        bundle = FormatBundle(maptype, tileformat)

        # build storage provider
        storage = make_cluster_storage(bundle, pyramid, **theme.storage)

        # build renderer provider
        renderer = make_metatile_renderer(bundle, pyramid, **theme.renderer)

        # build hybrid tile provider
        provider = HybridTileProvider(bundle, pyramid, storage, renderer)

        return MasonMap(name, metadata, provider)

