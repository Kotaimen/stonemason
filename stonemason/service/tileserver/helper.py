# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/4/15'

from stonemason.mason import Portrayal
from stonemason.mason.theme import Theme


def jsonify_portrayal(portrayal):
    assert isinstance(portrayal, Portrayal)
    template = {
        'name': portrayal.name,
        'metadata': {
            'title': portrayal.metadata.title,
            'version': portrayal.metadata.version,
            'abstract': portrayal.metadata.abstract,
            'attribution': portrayal.metadata.attribution,
            'center': portrayal.metadata.center,
            'center_zoom': portrayal.metadata.center_zoom
        },
        'maptype': portrayal.bundle.map_type,
        'tileformat': portrayal.bundle.tile_format,
        'pyramid': portrayal.pyramid,
        'schemas': []
    }

    for tag in portrayal.iter_schema():
        template['schemas'].append(tag)

    return template


def jsonify_map_theme(map_theme):
    assert isinstance(map_theme, Theme)
    return repr(map_theme)
