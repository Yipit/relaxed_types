from relaxed_types import typed_return, ReturnTypeError, Values, Or, And


def test_typed_return_with_verbose_predicate():
    def pred(x):
        if x == 10:
            pred.__doc__ = str("expectation matched.")
            return True
        else:
            pred.__doc__ = str("expected 10, got {}".format(x))
            return False
    decorator = typed_return(pred)

    @decorator
    def valid1():
        return 10

    @decorator
    def invalid1():
        return 0

    valid1()
    try:
        invalid1()
    except ReturnTypeError as e:
        assert str(e) == "expected 10, got 0"
    else:
        assert False, "did not raise ReturnTypeError"


def test_typed_return_with_static_values():
    decorator = typed_return(Values(1, 2))

    @decorator
    def valid1():
        return 1

    @decorator
    def valid2():
        return 2

    @decorator
    def invalid1():
        return 3

    valid1()
    valid2()
    try:
        invalid1()
    except ReturnTypeError as e:
        assert str(e) == 'Expected "3" to be in (1, 2)'
    else:
        assert False, "did not raise ReturnTypeError"


def test_or_predicate():
    decorator = typed_return(Or(int, float))

    @decorator
    def valid1():
        return 1

    @decorator
    def valid2():
        return 2.0

    @decorator
    def invalid1():
        return 's'

    valid1()
    valid2()
    try:
        invalid1()
    except ReturnTypeError as e:
        assert str(e) == """'s' did not match Or(<type 'int'>, <type 'float'>).
More details about the last check: Type mismatch for 's', expected <type 'float'>. Outer value: 's'"""
    else:
        assert False, "did not raise ReturnTypeError"


def test_and_predicate():
    def positive(x):
        positive.__doc__ = str("{} should be greater than 0".format(x))
        return x > 0

    decorator = typed_return(And(int, positive))

    @decorator
    def valid1():
        return 1

    @decorator
    def invalid1():
        return 2.0

    @decorator
    def invalid2():
        return 0

    valid1()

    try:
        invalid1()
    except ReturnTypeError as e:
        assert str(e) == """2.0 did not match And(<type 'int'>, {}).
More details about the last check: Type mismatch for 2.0, expected <type 'int'>. Outer value: 2.0""".format(positive)
    else:
        assert False, "did not raise ReturnTypeError"

    try:
        invalid2()
    except ReturnTypeError as e:
        assert str(e) == """0 did not match And(<type 'int'>, {}).
More details about the last check: 0 should be greater than 0""".format(positive)
    else:
        assert False, "did not raise ReturnTypeError"
