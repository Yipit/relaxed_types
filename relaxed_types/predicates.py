from .checks import check_type
from .exceptions import ReturnTypeError


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


def And(*expected_type):
    fn_name = str('And{}'.format(repr(expected_type)))

    def fn(value):
        for t in expected_type:
            try:
                check_type(value, t, value)
            except ReturnTypeError as e:
                fn.__doc__ = '{} did not match {}.\nMore details about the last check: {}'.format(repr(value), fn_name,
                                                                                                  str(e))
                return False
        return True

    fn.__name__ = fn_name
    return fn
