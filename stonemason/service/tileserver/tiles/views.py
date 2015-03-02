# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/27/15'

from werkzeug.http import http_date
from flask import abort, make_response, jsonify
from flask.views import MethodView

from ..models import MasonModel


class TilesView(MethodView):
    def __init__(self, mason_model):
        assert isinstance(mason_model, MasonModel)
        self._model = mason_model

    def get(self, tag, z, x, y, scale, ext):
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
    def __init__(self, mason_model):
        assert isinstance(mason_model, MasonModel)
        self._model = mason_model

    def get(self):
        tags = self._model.get_tile_tags()
        return jsonify(result=tags)



