# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/27/15'

from flask import Blueprint

from .views import MapBookView, TilesView


def create_blueprint(**kwargs):
    blueprint = Blueprint('maps', __name__, template_folder='templates')

    map_view = MapBookView.as_view('maps', **kwargs)

    blueprint.add_url_rule(
        endpoint='maps',
        rule='/maps/<theme>',
        view_func=map_view,
        methods=['GET']
    )

    blueprint.add_url_rule(
        endpoint='overview',
        rule='/',
        view_func=map_view,
        defaults={'theme': None},
        methods=['GET']
    )

    tiles_view = TilesView.as_view('tiles', **kwargs)

    blueprint.add_url_rule(
        endpoint='tile',
        rule='/tiles/<theme>/<int:z>/<int:x>/<int:y><tag>',
        view_func=tiles_view,
        methods=['GET']
    )

    return blueprint
