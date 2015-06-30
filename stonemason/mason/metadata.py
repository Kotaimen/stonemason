# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/9/15'

from collections import namedtuple


_Metadata = namedtuple(
    'Metadata', 'title version abstract attribution origin origin_zoom')


class Metadata(_Metadata):
    def __new__(cls, title='', version='', abstract='', attribution='',
                origin=None, origin_zoom=4):
        if origin is None:
            origin = (0, 0)

        return _Metadata.__new__(cls, title=title, version=version,
                                 abstract=abstract, attribution=attribution,
                                 origin=origin,
                                 origin_zoom=origin_zoom)

