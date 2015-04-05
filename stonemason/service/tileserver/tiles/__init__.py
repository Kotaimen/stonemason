# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/27/15'

from flask import Blueprint

from .views import TilesView


def create_blueprint(**kwargs):
    blueprint = Blueprint('mason', __name__)

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
