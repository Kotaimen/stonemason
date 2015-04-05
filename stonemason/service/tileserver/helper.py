# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/4/15'

from stonemason.mason import MasonMap
from stonemason.mason.theme import MapTheme


def render_mason_map(mason_map):
    assert isinstance(mason_map, MasonMap)
    template = {
        'name': mason_map.name,
        'metadata': {
            'version': mason_map.metadata.get('version', ''),
            'abstract': mason_map.metadata.get('abstract', ''),
            'attribution': mason_map.metadata.get('attribution', 'K&R'),
            'center': mason_map.metadata.get('center', (0, 0)),
            'center_zoom': mason_map.metadata.get('center_zoom', 6)
        },
        'provider': {
            'tileformat': {
                'extension': mason_map.provider.formatbundle.tile_format.extension,
                'mimetype': mason_map.provider.formatbundle.tile_format.mimetype
            },
            'pyramid': {
                'projcs': mason_map.provider.pyramid.projcs,
                'geogcs': mason_map.provider.pyramid.geogcs,
                'levels': mason_map.provider.pyramid.levels,
            }
        }
    }
    return template


def render_map_theme(map_theme):
    assert isinstance(map_theme, MapTheme)
    template = {
        'name': map_theme.name,
        'metadata': map_theme.metadata,
        'provider': {
            'maptype': map_theme.maptype,
            'tileformat': map_theme.tileformat,
            'pyrammid': map_theme.pyramid,
            'storage': map_theme.storage,
            'renderer': map_theme.renderer
        }
    }
    return template
