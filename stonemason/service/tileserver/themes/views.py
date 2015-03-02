# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/27/15'

from flask import jsonify
from flask.views import MethodView

from ..models import ThemeModel


class ThemeView(MethodView):
    def __init__(self, theme_model):
        assert isinstance(theme_model, ThemeModel)
        self._theme_model = theme_model

    def get(self, tag):
        if tag is None:
            collection = list()

            for theme in self._theme_model:
                collection.append(theme.describe())

            return jsonify(result=collection)

        else:
            theme = self._theme_model.get_theme(tag)
            return jsonify(result=theme.describe())

