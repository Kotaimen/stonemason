# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/27/15'

from flask import Blueprint

from .views import ThemeView


def create_blueprint(**kwargs):
    blueprint = Blueprint('themes', __name__)

    view = ThemeView.as_view('themes', **kwargs)

    blueprint.add_url_rule(
        endpoint='theme',
        rule='/themes/<tag>',
        view_func=view,
        methods=['GET']
    )

    blueprint.add_url_rule(
        endpoint='theme_list',
        rule='/themes',
        view_func=view,
        defaults={'tag': None},
        methods=['GET']
    )

    return blueprint
