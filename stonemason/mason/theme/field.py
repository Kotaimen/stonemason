# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme.field
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Field properties in a ThemeBlock.

"""

import six


class FieldTypeError(Exception):
    """Field Type Error"""
    pass


class BlockField(object):
    """Block Field Base

    A property field in a theme block. A property field can accept different
    validators to check the validity of its value.

    `key`

        A string literal identifies a field.

    `value`

        Arbitrary field value.

    :param key: Identifier of a block field.
    :type key: str
    :param value: Value of a block field.
    :type value: object

    """

    def __init__(self, key, value):
        self._key = key
        self._value = value

    @property
    def key(self):
        """Returns identifier of a block field"""
        return self._key

    @property
    def value(self):
        """Returns value of a block field"""
        return self._value

    def validate(self, *validators):
        """Validate the value of the block field"""
        for v in validators:
            v(self.value)


    def __repr__(self):
        return "%s(key=%r, value=%r)" % (
            self.__class__.__name__, self._key, self._value)


class IntegerBlockField(BlockField):
    """Integer Block Field

    A block field contains a integer as its value.

    :param key: Identifier of a field.
    :type key: str
    :param value: A integer.
    :type value: int

    """

    def __init__(self, key, value):
        if not isinstance(value, six.integer_types):
            raise FieldTypeError('Field %s should be a integer!' % key)
        BlockField.__init__(self, key, value)


class StringBlockField(BlockField):
    """String Block Field

    A block field contains a string as its value.

    :param key: Identifier of a field.
    :type key: str
    :param value: A string literal.
    :type value: str

    """

    def __init__(self, key, value):
        if not isinstance(value, six.string_types):
            raise FieldTypeError('Field %s should be a string!' % key)
        BlockField.__init__(self, key, value)


class ListBlockField(BlockField):
    """List Block Field

    A block field contains a list as its value.

    :param key: Identifier of a field.
    :type key: str
    :param value: A list object.
    :type value: list

    """

    def __init__(self, key, value):
        if not isinstance(value, list):
            raise FieldTypeError('Field %s should be a list!' % key)
        BlockField.__init__(self, key, value)

    def validate(self, *validators):
        for item in self._value:
            for validator in validators:
                validator(item)

class DictBlockField(BlockField):
    """Dict Block Field

    A block field contains a dict as its value.

    :param key: Identifier of a field.
    :type key: str
    :param value: A dict object.
    :type value: dict

    """

    def __init__(self, key, value):
        if not isinstance(value, dict):
            raise FieldTypeError('Field %s should be a dict!' % key)
        BlockField.__init__(self, key, value)

    def validate(self, *validators):
        for item in six.iteritems(self._value):
            for validator in validators:
                validator(item)
