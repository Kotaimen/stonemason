# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/27/15'

from flask import Blueprint

from .views import MapView, TilesView


def create_blueprint(**kwargs):
    blueprint = Blueprint('maps', __name__, template_folder='templates')

    map_view = MapView.as_view('maps', **kwargs)

    blueprint.add_url_rule(
        endpoint='maps',
        rule='/maps/<tag>',
        view_func=map_view,
        methods=['GET']
    )

    blueprint.add_url_rule(
        endpoint='overview',
        rule='/',
        view_func=map_view,
        defaults={'tag': None},
        methods=['GET']
    )

    tiles_view = TilesView.as_view('tiles', **kwargs)

    blueprint.add_url_rule(
        endpoint='tile',
        rule='/tiles/<tag>/<int:z>/<int:x>/<int:y>@<scale>.<ext>',
        view_func=tiles_view,
        methods=['GET']
    )

    blueprint.add_url_rule(
        endpoint='tile@1x',
        rule='/tiles/<tag>/<int:z>/<int:x>/<int:y>.<ext>',
        view_func=tiles_view,
        defaults={'scale': '1x'},
        methods=['GET']
    )

    return blueprint
