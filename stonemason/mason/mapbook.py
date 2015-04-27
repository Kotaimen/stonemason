# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/9/15'

import six

from .metadata import Metadata
from .mapsheet import MapSheet


class MapBook(object):
    def __init__(self, name, metadata=None, map_sheets=None):
        self._name = name

        if metadata is None:
            metadata = Metadata()

        assert isinstance(metadata, Metadata)
        self._metadata = metadata

        if map_sheets is None:
            map_sheets = dict()

        assert isinstance(map_sheets, dict)
        self._map_sheets = map_sheets

    @property
    def name(self):
        return self._name

    @property
    def metadata(self):
        return self._metadata

    def put_map_sheet(self, tag, sheet):
        assert isinstance(sheet, MapSheet)
        self._map_sheets[tag] = sheet

    def get_map_sheet(self, tag):
        return self._map_sheets.get(tag)

    def has_map_sheet(self, tag):
        return tag in self._map_sheets

    def iter_map_sheets(self):
        return iter(self._map_sheets)
