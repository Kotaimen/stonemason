# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '3/2/15'

from flask.views import MethodView
from flask import render_template

from ..models import MasonModel, ThemeModel


class AdminView(MethodView):
    def __init__(self, mason_model, theme_model):
        assert isinstance(mason_model, MasonModel)
        assert isinstance(theme_model, ThemeModel)
        self._mason_model = mason_model
        self._theme_model = theme_model

    def get(self):
        collection = list()
        for tag in self._mason_model.get_tile_tags():
            theme = self._theme_model.get_theme(tag)
            collection.append(theme.describe())

        return render_template('index.html', themes=collection)
