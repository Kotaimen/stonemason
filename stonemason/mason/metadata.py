# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/9/15'

from collections import namedtuple


_Metadata = namedtuple(
    'Metadata', 'title version abstract attribution center center_zoom')


class Metadata(_Metadata):
    def __new__(cls, title='', version='', abstract='', attribution='',
                center=None, center_zoom=4):
        if center is None:
            center = (0, 0)

        return _Metadata.__new__(cls, title=title, version=version,
                                 abstract=abstract, attribution=attribution,
                                 center=center,
                                 center_zoom=center_zoom)

