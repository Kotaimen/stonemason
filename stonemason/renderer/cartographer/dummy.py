# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/25/15'

from ..map import BaseLayer, TransformLayer, CompositeLayer
from stonemason.renderer.map import ImageMapRenderer, RasterMapRenderer, \
    VectorMapRenderer


class DummyBaseRenderer(
    BaseLayer, ImageMapRenderer, RasterMapRenderer, VectorMapRenderer):
    def image(self, context):
        return None

    def raster(self, context):
        return None

    def vector(self, context):
        return None


class DummyTransformRenderer(
    TransformLayer, ImageMapRenderer, RasterMapRenderer, VectorMapRenderer):
    def image(self, context):
        return None

    def raster(self, context):
        return None

    def vector(self, context):
        return None


class DummyCompositeRenderer(
    CompositeLayer, ImageMapRenderer, RasterMapRenderer, VectorMapRenderer):
    def image(self, context):
        return None

    def raster(self, context):
        return None

    def vector(self, context):
        return None
