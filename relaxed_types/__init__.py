# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import functools
import inspect


Any = object()


def check_type(value, expected_type, outer_value, extra=None):
    if expected_type is Any:
        return
    elif isinstance(expected_type, list):
        if not isinstance(value, list):
            fail(value, expected_type, outer_value)

        for t in expected_type:
            for v in value:
                check_type(v, t, outer_value)

    elif isinstance(expected_type, dict):
        if not isinstance(value, dict):
            fail(value, expected_type, outer_value)

        for key_name, key_type in expected_type.items():
            if key_name not in value:
                fail(value, expected_type, outer_value)
            check_type(value[key_name], key_type, outer_value)

    elif isinstance(expected_type, tuple):
        if not isinstance(value, tuple):
            fail(value, expected_type, outer_value)

        if len(value) != len(expected_type):
            fail(value, expected_type, outer_value)

        for v, t in zip(value, expected_type):
            check_type(v, t, outer_value)

    elif inspect.isclass(expected_type):
        if not isinstance(value, expected_type):
            fail(value, expected_type, outer_value)
    else:
        if not expected_type(value):
            fail(value, expected_type, outer_value)
    if extra:
        if not extra(value):
            fail(value, expected_type, outer_value)


def typed_return(expected_type, extra=None):
    def wrapper(fn):
        @functools.wraps(fn)
        def newfn(*args, **kw):
            result = fn(*args, **kw)
            check_type(result, expected_type, outer_value=result, extra=extra)
            return result
        return newfn
    return wrapper


def fail(value, expected_type, outer_value):
    raise ReturnTypeError("Type mismatch for {}, expected {}. Outer value: {}".format(
        short_repr(value), expected_type, short_repr(outer_value)), value)


def short_repr(obj):
    s = repr(obj)
    limit = 1000
    if len(s) > limit:
        return s[:limit] + '... [CONTENT TOO LONG]'
    else:
        return s[:limit]


class ReturnTypeError(TypeError):
    def __init__(self, msg, value):
        super(ReturnTypeError, self).__init__(msg)
        self.value = value
