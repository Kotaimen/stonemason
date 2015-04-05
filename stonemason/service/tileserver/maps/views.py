# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/2/15'

from flask.views import MethodView
from flask import render_template, abort

from ..models import MasonModel, ThemeModel
from ..helper import render_mason_map


class MapView(MethodView):
    """Map View

    A map site with named tag.

    :param mason_model: A :class:`~stonemason.service.models.MasonModel` that
                        contains mason themes.
    :type mason_model: :class:`~stonemason.service.models.MasonModel`

    :param theme_model: A theme model that manages themes.
    :type theme_model: :class:`~stonemason.service.models.ThemeModel`

    """

    def __init__(self, mason_model, theme_model):
        assert isinstance(mason_model, MasonModel)
        assert isinstance(theme_model, ThemeModel)
        self._mason_model = mason_model
        self._theme_model = theme_model

    def get(self, tag):
        """Retrieve a map site with the given tag."""
        mason_map = self._mason_model.get_map(tag)
        if mason_map is None:
            abort(404)

        return render_template(
            'map.html', mason_map=render_mason_map(mason_map))
