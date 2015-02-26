# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme.element
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements the base element of the theme.

"""

__author__ = 'ray'
__date__ = '2/23/15'


class ThemeElement(object):
    """Base Element of a Theme

    A `ThemeElement` represents the base building block of a theme. Both user
    defined attributes and child elements could be attached to a
    `ThemeElement`.

    :param name: A string literal represents the name of the `ThemeElement`.
    :type name: str

    :param attributes: A dict object contains attributes of the `ThemeElement`.
    :type attributes: str

    """
    def __init__(self, name, **attributes):
        self._name = name
        self._attributes = attributes
        self._children = dict()

    @property
    def name(self):
        """Name of the `ThemeElement`

        :return: A string literal represents the name of the `ThemeElement`.
        :rtype: str

        """
        return self._name

    @property
    def attributes(self):
        """Attributes of the `ThemeElement`

        :return: A dict object contains attributes of the `ThemeElement`.
        :rtype: dict

        """
        return self._attributes

    def validate(self):
        """Validate the attributes of the `ThemeElement`

        :return: Return true if no error, otherwise raise errors.
        :rtype: bool

        """
        for sub in self._children:
            sub.validate()
        return True

    def put_element(self, name, elem):
        """Add a child `ThemeElement`

        :param name: A string literal represents the name of the `ThemeElement`.
        :type name: str

        :param elem: A `ThemeElement` instance.
        :type elem: `ThemeElement`

        """
        assert isinstance(elem, ThemeElement)
        self._children[name] = elem

    def has_element(self, name):
        """Check if has child `ThemeElement` with the given name

        :param name: A string literal represents the name of the `ThemeElement`.
        :type name: str

        :return: Return True if exists.
        :rtype: bool

        """
        return name in self._children

    def get_element(self, name):
        """Get a child `ThemeElement`

        :param name: A string literal represents the name of the `ThemeElement`.
        :type name: str

        :return: A `ThemeElement` instance or ``None`` if not exists.
        :rtype: `ThemeElement` or None

        """
        return self._children.get(name, None)

    def __repr__(self):
        """A printable representation of the `ThemeElement`.

        :return: A string literal representation of the `ThemeElement`.
        :rtype: str

        """
        repr_attr = ', '.join(
            '%s=%r' % (key, val) for key, val in self._attributes.items())
        return '%s(name=%s, %s)' % (
            self.__class__.__name__, self._name, repr_attr)
