# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/2/15'

from flask.views import MethodView
from flask import render_template, abort

from ..models import MasonModel, ThemeModel


class MapView(MethodView):
    def __init__(self, mason_model, theme_model):
        assert isinstance(mason_model, MasonModel)
        assert isinstance(theme_model, ThemeModel)
        self._mason_model = mason_model
        self._theme_model = theme_model

    def get(self, tag):

        tags = self._mason_model.get_tile_tags()
        if tag not in tags:
            abort(404)

        theme = self._theme_model.get_theme(tag)

        return render_template('map.html', theme=theme.describe())
