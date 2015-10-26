# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/9/15'

import time

from stonemason.pyramid import MetaTileIndex, MetaTile, TileCluster
from stonemason.pyramid.geo import TileMapSystem
from stonemason.renderer import MasonRenderer, RenderContext
from stonemason.storage.tilestorage import ClusterStorage, MetaTileStorageConcept


class MapSheet(object):
    def __init__(self, tag, bundle, pyramid, readonly=False):
        self._tag = tag
        self._bundle = bundle
        self._pyramid = pyramid
        self._readonly = readonly

    @property
    def tag(self):
        return self._tag

    @property
    def bundle(self):
        return self._bundle

    @property
    def pyramid(self):
        return self._pyramid

    @property
    def readonly(self):
        return self._readonly

    @readonly.setter
    def readonly(self, val):
        self._readonly = val

    def get_tilecluster(self, meta_index):
        raise NotImplementedError

    def render_metatile(self, meta_index):
        raise NotImplementedError


class ClusterMapSheet(MapSheet):
    def __init__(self, tag, bundle, pyramid, storage, renderer):
        MapSheet.__init__(self, tag, bundle, pyramid)
        assert isinstance(storage, ClusterStorage)
        assert isinstance(renderer, MasonRenderer)
        self._storage = storage
        self._renderer = renderer

    def get_tilecluster(self, meta_index):
        storage_meta_index = MetaTileIndex(meta_index.z,
                                           meta_index.x,
                                           meta_index.y,
                                           self._storage.stride)
        cluster = self._storage.get(storage_meta_index)
        if cluster is not None:
            return cluster

        if self.readonly:
            return None

        feature = self.get_feature(meta_index)
        if feature is None:
            return None

        metadata = dict(
            mimetype=self._bundle.tile_format.mimetype,
            mtime=time.time()
        )

        cluster = TileCluster.from_feature(
            meta_index, feature.data, metadata, self._bundle.writer, 0)

        return cluster

    def get_feature(self, meta_index):
        tms = TileMapSystem(self._pyramid)

        context = RenderContext(
            map_proj=tms.pyramid.projcs,
            map_bbox=tms.calc_tile_envelope(meta_index),
            map_size=(meta_index.stride * 256, meta_index.stride * 256),
            meta_index=meta_index,
        )

        feature = self._renderer.render(context)
        if feature is None:
            return None

        return feature

    def render_metatile(self, meta_index):
        if self._storage.get(meta_index) is not None:
            return True

        feature = self.get_feature(meta_index)
        if feature is None:
            return False

        data = self._bundle.writer.crop_map(feature.data, buffer=0)

        metatile = MetaTile(
            index=meta_index,
            mimetype=self._bundle.tile_format.mimetype,
            mtime=time.time(),
            data=data,
        )

        self._storage.put(metatile)

        return True


class MetaTileMapSheet(MapSheet):
    def __init__(self, tag, bundle, pyramid, storage, renderer):
        MapSheet.__init__(self, tag, bundle, pyramid)
        assert isinstance(storage, MetaTileStorageConcept)
        assert isinstance(renderer, MasonRenderer)
        self._storage = storage
        self._renderer = renderer

    def get_tilecluster(self, meta_index):
        storage_meta_index = MetaTileIndex(meta_index.z,
                                           meta_index.x,
                                           meta_index.y,
                                           self._storage.stride)
        metatile = self._storage.get(storage_meta_index)
        if metatile is not None:
            cluster = TileCluster.from_metatile(metatile, self.bundle.writer)
            return cluster

        if self.readonly:
            return None

        feature = self.get_feature(meta_index)
        if feature is None:
            return None

        metadata = dict(
            mimetype=self._bundle.tile_format.mimetype,
            mtime=time.time()
        )

        cluster = TileCluster.from_feature(
            meta_index, feature.data, metadata, self._bundle.writer, 0)

        return cluster

    def get_feature(self, meta_index):
        tms = TileMapSystem(self._pyramid)

        context = RenderContext(
            map_proj=tms.pyramid.projcs,
            map_bbox=tms.calc_tile_envelope(meta_index),
            map_size=(meta_index.stride * 256, meta_index.stride * 256),
            meta_index=meta_index,
        )

        feature = self._renderer.render(context)
        if feature is None:
            return None

        return feature

    def render_metatile(self, meta_index):
        if self._storage.get(meta_index) is not None:
            return True

        feature = self.get_feature(meta_index)
        if feature is None:
            return False

        data = self._bundle.writer.crop_map(feature.data, buffer=0)

        metatile = MetaTile(
            index=meta_index,
            mimetype=self._bundle.tile_format.mimetype,
            mtime=time.time(),
            data=data,
        )

        self._storage.put(metatile)

        return True
