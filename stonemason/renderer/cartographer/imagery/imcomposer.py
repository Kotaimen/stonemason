# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/22/15'

from ...layerexpr import CompositeLayer
from ...context import RenderContext
from ...feature import ImageFeature

from .imagemagick import ImageMagickComposer


class IMComposer(CompositeLayer):
    PROTOTYPE = 'imagemagick'

    def __init__(self, name, layers, command=None, tempdir=None, tempfmt='png'):
        CompositeLayer.__init__(self, name, layers)
        self._composer = ImageMagickComposer(
            command,
            export_format=tempfmt,
            import_format=tempfmt,
            tempdir=tempdir)

    def render(self, context):
        assert isinstance(context, RenderContext)

        sources = dict((l.name, l.render(context).data) for l in self._layers)

        result = self._composer.compose(sources)

        return ImageFeature(
            crs=context.map_proj,
            bounds=context.map_bbox,
            size=context.map_size,
            data=result)
