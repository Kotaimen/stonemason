# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '2/27/15'

from flask import Blueprint

from .views import TilesView, TagsView


def create_blueprint(**kwargs):
    tiles = Blueprint('tiles', __name__)

    tiles_view = TilesView.as_view('tiles', **kwargs)

    tiles.add_url_rule(
        rule='/tiles/<tag>/<int:z>/<int:x>/<int:y>@<scale>.<ext>',
        view_func=tiles_view,
        methods=['GET']
    )

    tiles.add_url_rule(
        rule='/tiles/<tag>/<int:z>/<int:x>/<int:y>.<ext>',
        view_func=tiles_view,
        defaults={'scale': '1x'},
        methods=['GET']
    )

    tags_view = TagsView.as_view('tags', **kwargs)

    tiles.add_url_rule(
        rule='/tiles',
        view_func=tags_view,
        methods=['GET']
    )

    return tiles
