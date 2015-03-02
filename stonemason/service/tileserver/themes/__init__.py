# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/27/15'

from flask import Blueprint

from .views import ThemeView


def create_blueprint(**kwargs):
    themes = Blueprint('themes', __name__)

    themes_view = ThemeView.as_view('themes', **kwargs)

    themes.add_url_rule(
        rule='/themes/<tag>',
        view_func=themes_view,
        methods=['GET']
    )

    themes.add_url_rule(
        rule='/themes',
        view_func=themes_view,
        defaults={'tag': None},
        methods=['GET']
    )

    return themes
