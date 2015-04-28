# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/9/15'


from collections import OrderedDict

from .metadata import Metadata
from .mapsheet import MapSheet


class MapBook(object):
    def __init__(self, name, metadata=None, map_sheets=None):
        self._name = name

        if metadata is None:
            metadata = Metadata()

        assert isinstance(metadata, Metadata)
        self._metadata = metadata

        self._map_sheets = OrderedDict()
        if map_sheets is not None:
            assert isinstance(map_sheets, dict)
            self._map_sheets.update(map_sheets)

    @property
    def name(self):
        return self._name

    @property
    def metadata(self):
        return self._metadata

    def tags(self):
        return self._map_sheets.keys()

    def sheets(self):
        return self._map_sheets.values()

    def items(self):
        return self._map_sheets.items()

    def __setitem__(self, tag, sheet):
        assert isinstance(sheet, MapSheet)
        self._map_sheets[tag] = sheet

    def __getitem__(self, tag):
        return self._map_sheets[tag]

    def __contains__(self, tag):
        return tag in self._map_sheets
