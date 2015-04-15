# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/9/15'

from stonemason.tilestorage import ClusterStorage, TileCluster
from stonemason.renderer.tilerenderer import MetaTileRenderer


class Schema(object):
    def __init__(self, tag):
        self._tag = tag

    @property
    def tag(self):
        return self._tag

    def get_metatile(self, bundle, pyramid, meta_index):
        raise NotImplementedError

    def get_tilecluster(self, bundle, pyramid, meta_index):
        raise NotImplementedError

    def render_metatile(self, bundle, pyramid, meta_index):
        raise NotImplementedError


class NullSchema(Schema):
    def __init__(self, tag='null'):
        Schema.__init__(self, tag)

    def get_metatile(self, bundle, pyramid, meta_index):
        return None

    def get_tilecluster(self, bundle, pyramid, meta_index):
        return None

    def render_metatile(self, bundle, pyramid, meta_index):
        return False


class HybridSchema(Schema):
    def __init__(self, tag, storage, renderer):
        Schema.__init__(self, tag)
        assert isinstance(storage, ClusterStorage)
        assert isinstance(renderer, MetaTileRenderer)
        self._storage = storage
        self._renderer = renderer

    def get_tilecluster(self, bundle, pyramid, meta_index):
        cluster = self._storage.get(meta_index)
        if cluster is not None:
            return cluster

        metatile = self.get_metatile(bundle, pyramid, meta_index)
        if metatile is None:
            return None

        cluster = TileCluster.from_metatile(metatile, bundle.writer)
        return cluster

    def get_metatile(self, bundle, pyramid, meta_index):
        metatile = self._renderer.render_metatile(meta_index)
        return metatile

    def render_metatile(self, bundle, pyramid, meta_index):
        if self._storage.get(meta_index) is not None:
            return True
        result = self._renderer.render_metatile(meta_index)
        if result:
            self._storage.put(result)
            return True
        else:
            return False
