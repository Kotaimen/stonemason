# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/27/15'

from werkzeug.http import http_date
from flask import abort, make_response, jsonify
from flask.views import MethodView

from ..models import MasonModel


class TilesView(MethodView):
    """Tile View

    Get Map Tile with a tag, zoom level and (x, y) coordinates. Raise
    :http:statuscode:`400` when request is not valid.

    :param mason_model: A :class:`~stonemason.service.models.MasonModel` that
                        contains mason themes.
    :type mason_model: :class:`~stonemason.service.models.MasonModel`

    """

    def __init__(self, mason_model):
        assert isinstance(mason_model, MasonModel)
        self._model = mason_model

    def get(self, tag, z, x, y, scale, ext):
        """Return a tile data and raise :http:statuscode:`404` if not found.

        :param tag: The Name of a theme. A string literal that uniquely
                    identify a theme.
        :type tag: str

        :param z: A positive integer that represents the zoom level of a tile.
        :type z: int

        :param x: A positive integer that represents the coordinate along x
                  axis. A valid value could be 0 to :math:`2^z - 1`.
        :type x: int

        :param y: A positive integer that represents the coordinate along y
                  axis. A valid would be 0 to :math:`2^z - 1`.
        :type y: int

        :param scale: A positive integer that scales elements like font, stroke
                      during rendering process for display on high resolution
                      device.
        :type scale: str

        :param ext: A string literal that indicates the output format of the
                    requested tile.
        :type ext: str

        """

        tile = self._model.mason.get_tile(tag, z, x, y, scale, ext)
        if tile is None:
            abort(404)

        response = make_response(tile.data)

        # set response headers
        response.headers['Content-Type'] = tile.mimetype
        response.headers['ETag'] = tile.etag
        response.headers['Last-Modified'] = http_date(tile.mtime)
        response.headers['Cache-Control'] = 'public, max-age=86400'

        return response


class TagsView(MethodView):
    """Tag View

    Get loaded theme names.

    :param mason_model: A :class:`~stonemason.service.models.MasonModel` that
                        contains mason themes.
    :type mason_model: :class:`~stonemason.service.models.MasonModel`

    """

    def __init__(self, mason_model):
        assert isinstance(mason_model, MasonModel)
        self._model = mason_model

    def get(self):
        """Get a list of loaded theme names"""
        tags = self._model.get_tile_tags()
        return jsonify(result=tags)



