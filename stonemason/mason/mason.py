# -*- encoding: utf-8 -*-
"""
    stonemason.mason.mason
    ~~~~~~~~~~~~~~~~~~~~~~

    Facade StoneMason.

"""


class Mason(object):
    """Stonemason Facade"""

    def get_theme(self, tag):
        return dict(name=tag)

    def get_themes(self):
        return []

    def get_tile(self, tag, z, x, y, scale, ext):
        return 'Tile(%s, %s, %d, %d, %s, %s)' % (tag, z, x, y, scale, ext)

