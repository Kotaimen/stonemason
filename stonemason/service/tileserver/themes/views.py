# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/27/15'

from flask import jsonify, abort
from flask.views import MethodView

from ..models import ThemeModel
from ..helper import render_map_theme


class ThemeView(MethodView):
    """ Theme View

    Retrieve description of a list of available themes.

    :param theme_model: A theme model that manages themes.
    :type theme_model: :class:`~stonemason.service.models.ThemeModel`

    """

    def __init__(self, theme_model):
        assert isinstance(theme_model, ThemeModel)
        self._theme_model = theme_model

    def get(self, tag):
        """Return description of the theme. Raise :http:statuscode:`404` if
        not found.

        :param name: Name of a theme.
        :type name: str

        """

        if tag is None:
            collection = list()

            for theme in self._theme_model:
                collection.append(render_map_theme(theme))

            return jsonify(result=collection)

        else:
            theme = self._theme_model.get_theme(tag)
            if theme is None:
                abort(404)

            return jsonify(result=render_map_theme(theme))

