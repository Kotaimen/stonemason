# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/27/15'

from flask import Blueprint

from .views import MapView


def create_blueprint(**kwargs):
    blueprint = Blueprint('maps', __name__, template_folder='templates')

    view = MapView.as_view('maps', **kwargs)

    blueprint.add_url_rule(
        endpoint='maps',
        rule='/maps/<tag>',
        view_func=view,
        methods=['GET']
    )

    return blueprint
