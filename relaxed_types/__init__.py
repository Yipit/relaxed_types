# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import functools
import inspect


Any = object()


def typed_return(expected_type, extra=None):
    def wrapper(fn):
        @functools.wraps(fn)
        def newfn(*args, **kw):
            result = fn(*args, **kw)
            check_type(result, expected_type, outer_value=result, extra=extra)
            return result
        return newfn
    return wrapper


def check_type(value, expected_type, outer_value, extra=None):
    if expected_type is Any:
        return
    elif isinstance(expected_type, list):
        _check_list(value, expected_type, outer_value)
    elif isinstance(expected_type, dict):
        _check_dict(value, expected_type, outer_value)
    elif isinstance(expected_type, tuple):
        _check_tuple(value, expected_type, outer_value)
    elif isinstance(expected_type, set):
        _check_set(value, expected_type, outer_value)
    elif inspect.isclass(expected_type):
        _check_any_type(value, expected_type, outer_value)
    else:
        _check_predicate(value, expected_type, outer_value)

    if extra:
        _check_predicate(value, extra, outer_value)


def _check_any_type(value, expected_type, outer_value):
    if not isinstance(value, expected_type):
        _fail(value, expected_type, outer_value)


def _check_predicate(value, expected_type, outer_value):
    if not expected_type(value):
        _fail(value, expected_type, outer_value, msg=expected_type.__doc__)


def _check_tuple(value, expected_type, outer_value):
    if not isinstance(value, tuple):
        _fail(value, expected_type, outer_value)
    if len(value) != len(expected_type):
        _fail(value, expected_type, outer_value)
    for v, t in zip(value, expected_type):
        check_type(v, t, outer_value)


def _check_list(value, expected_type, outer_value):
    if not isinstance(value, list):
        _fail(value, expected_type, outer_value)
    for t in expected_type:
        for v in value:
            check_type(v, t, outer_value)


def _check_set(value, expected_type, outer_value):
    if not isinstance(value, set):
        _fail(value, expected_type, outer_value)
    for t in expected_type:
        for v in value:
            check_type(v, t, outer_value)


def _check_dict(value, expected_type, outer_value):
    if not isinstance(value, dict):
        _fail(value, expected_type, outer_value)
    if Any in expected_type:
        unspecified_type = expected_type[Any]
        for key_name in value.keys():
            check_type(value[key_name], expected_type.get(key_name, unspecified_type), outer_value)
    else:
        expected_keys = set(expected_type.keys())
        value_keys = set(value.keys())
        if len(expected_keys) > len(value_keys):
            _fail(value, expected_type, outer_value, msg='Expected keys {} to exist'.format(list(expected_keys - value_keys)))
        elif len(expected_keys) < len(value_keys):
            _fail(value, expected_type, outer_value, msg='Did not expect keys {} to exist'.format(list(value_keys - expected_keys)))
        for key_name in expected_type.keys():
            check_type(value[key_name], expected_type[key_name], outer_value)


def _fail(value, expected_type, outer_value, msg=None):
    if msg is None:
        msg = "Type mismatch for {}, expected {}. Outer value: {}".format(
            _short_repr(value), expected_type, _short_repr(outer_value))
    raise ReturnTypeError(msg, value)


def _short_repr(obj):
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


def Values(*values):
    def fn(value):
        fn.__doc__ = 'Expected "{}" to be in {}'.format(value, values)
        return value in values
    fn.__name__ = str("Values{}".format(repr(values)))
    return fn


def Or(*expected_type):
    fn_name = str('Or{}'.format(repr(expected_type)))

    def fn(value):
        failed = False
        for t in expected_type:
            try:
                check_type(value, t, value)
            except ReturnTypeError as e:
                failed = True
                fn.__doc__ = '{} did not match {}.\nMore details about the last check: {}'.format(repr(value), fn_name, str(e))
            else:
                failed = False
                fn.__doc__ = "{} matched {}".format(value, t)
                break
        return not failed

    fn.__name__ = fn_name
    return fn
