# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '4/9/15'

from stonemason.pyramid import Pyramid
from stonemason.provider.formatbundle import FormatBundle

from .metadata import Metadata
from .schema import Schema


class Portrayal(object):
    def __init__(self, name, metadata, bundle, pyramid, schemas=None):
        assert isinstance(metadata, Metadata)
        assert isinstance(bundle, FormatBundle)
        assert isinstance(pyramid, Pyramid)

        self._name = name
        self._metadata = metadata
        self._bundle = bundle
        self._pyramid = pyramid

        if schemas is None:
            schemas = dict()

        self._schemas = schemas

    @property
    def name(self):
        return self._name

    @property
    def metadata(self):
        return self._metadata

    @property
    def bundle(self):
        return self._bundle

    @property
    def pyramid(self):
        return self._pyramid

    def put_schema(self, tag, schema):
        assert isinstance(schema, Schema)
        self._schemas[tag] = schema

    def get_schema(self, tag):
        return self._schemas.get(tag)

    def has_schema(self, tag):
        return tag in self._schemas

    def iter_schema(self):
        return iter(self._schemas)

