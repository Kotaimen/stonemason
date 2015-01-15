# -*- encoding: utf-8 -*-
"""
    stonemason.mason.config.config
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements the config of stonemason.

"""
import os
import six
import importlib

from .configparser import ConfigParser, ConfigParserError


class ConfigError(Exception):
    pass


class FileNotFound(ConfigError):
    pass


class InvalidConfig(ConfigError):
    pass


class Config(dict):
    """A dict-like config object Configuration

    The Config is a dict like configuration object with some additional
    functions. It can be set from files or stream of different format that
    defined in :class:`~stonemason.mason.config.grammar` module and from
    python object.

    The Config does not interpret the contents of a config. It just
    translates supported file formats into a dict.

    Sample:

    >>> from stonemason.mason.config import Config
    >>> obj = dict(name='stonemason')
    >>> conf = Config()
    >>> conf.read_from_dict(obj)
    True
    >>> conf['name']
    'stonemason'

    """

    def read_from_file(self, filename):
        """Read config from a file.

        Read config from a file and return true if succeed.

        :param filename: The name of the config file.
        :type filename: str
        :return: return true if succeed.
        :returns: bool
        """
        if not os.path.exists(filename):
            raise FileNotFound("Config file not found: %s." % filename)

        with open(filename) as fp:
            return self.read_from_stream(fp)


    def read_from_stream(self, fp):
        """Read config from stream.

        Read config from a file-like object and return true if succeed.

        :param fp: A file-like object.
        :type fp: FileIO
        :return: return true if succeed.
        :returns: bool
        """

        p = ConfigParser()
        try:
            properties = p.parse(fp.read())
        except ConfigParserError:
            raise InvalidConfig

        self.update(properties)
        return True


    def read_from_object(self, obj):
        """Read config from a python object.

        Read config from a python object and return true if succeed.

        :param obj: A python object.
        :type obj: object
        :return: Return true if succeed.
        :returns: bool
        """
        if isinstance(obj, six.string_types):
            obj = importlib.import_module(obj)
        for key in dir(obj):
            self[key] = getattr(obj, key)
        return True

    def read_from_dict(self, obj):
        """Read config from a dict object.

        Read config from a dict object and return true if succeed.

        :param obj: A python dict.
        :type obj: object
        :return: Return true if succeed.
        :returns: bool
        """
        assert isinstance(obj, dict)
        self.update(obj)
        return True
