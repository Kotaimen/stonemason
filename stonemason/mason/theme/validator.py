# -*- encoding: utf-8 -*-
"""
    stonemason.mason.theme.validator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements a fleet of theme validators.

"""

import re
import six


class ValidationError(Exception):
    """Raise when validation failed."""
    pass


class Validator(object): # pragma: no cover
    """Validator Base

    A validator checks if a value fulfill some
    conditions. It will raise `ValidationError` if fails.
    """

    def __call__(self, value):
        """Raises `ValidationError` if fails. Otherwise, returns `True`.

        Subclasses should implement the detail of this method.
        """
        raise NotImplementedError


class ExprValidator(Validator):
    """Regular Expression Validator

    Validate a value against a regular expression.
    """

    def __init__(self, expr):
        self._expr = expr

    def __call__(self, value):
        """Returns true if is valid, otherwise raises `ValidationError`."""
        assert isinstance(value, six.string_types)

        if not re.match(self._expr, value):
            raise ValidationError(
                '%r not match regular expression %r!' % (value, self._expr)
            )

        return True


class MaxValueValidator(Validator):
    """Max Value Validator

    Validate if a value exceeds the max value.
    """

    def __init__(self, max_value):
        self._max_value = max_value

    def __call__(self, value):
        """Returns true if is valid, otherwise raises `ValidationError`."""
        assert isinstance(value, (six.integer_types, float))

        if value > self._max_value:
            raise ValidationError(
                '%r exceeds max value %r!' % (value, self._max_value)
            )

        return True


class MinValueValidator(Validator):
    """Max Value Validator

    Validate if a value exceeds the max value.
    """

    def __init__(self, min_value):
        self._min_value = min_value

    def __call__(self, value):
        """Raises `ValidationError` if not valid."""
        assert isinstance(value, (six.integer_types, float))

        if value < self._min_value:
            raise ValidationError(
                '%r exceeds min value %r!' % (value, self._min_value)
            )

        return True


class Power2Validator(Validator):
    """Powers of 2 Validator

    Validate if the value is powers of 2.
    """

    def __call__(self, value):
        """Raises `ValidationError` if not valid."""
        assert isinstance(value, six.integer_types)

        if ((value & (value - 1)) != 0) or value <= 0:
            raise ValidationError(
                '%r is not powers of 2!' % value
            )


class ChoiceValidator(Validator):
    """Choice Validation

    Validate if the value is in a specified choice.
    """

    def __init__(self, expected):
        self._expected = expected

    def __call__(self, value):
        """Raises `ValidationError` if not valid."""
        if value not in self._expected:
            raise ValidationError(
                '%r should be any of %r' % (value, self._expected)
            )
