# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import functools

from .checks import check_type, Any  # noqa
from .exceptions import ReturnTypeError  # noqa
from .predicates import *  # noqa


def typed_return(expected_type, extra=None):
    def wrapper(fn):
        @functools.wraps(fn)
        def newfn(*args, **kw):
            result = fn(*args, **kw)
            check_type(result, expected_type, outer_value=result, extra=extra)
            return result
        return newfn
    return wrapper
