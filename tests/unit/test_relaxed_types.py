import pytest

from relaxed_types import typed_return, ReturnTypeError, Any
from relaxed_types.types import MinLength, Range, Contains, RegExpPattern


def test_typed_return_with_simple_types():
    decorator = typed_return(int)

    @decorator
    def int_valid():
        return 1

    @decorator
    def int_invalid():
        return '1'

    assert int_valid() == 1
    pytest.raises(ReturnTypeError, int_invalid)


def test_typed_return_with_typing_types():
    decorator = typed_return(Any)

    @decorator
    def int_valid():
        return 1

    @decorator
    def str_valid():
        return 'string'

    assert int_valid() == 1
    assert str_valid() == 'string'


def test_typed_return_with_compound_types():
    decorator = typed_return([int])

    @decorator
    def list_of_ints_valid():
        return [1, 2, 3]

    @decorator
    def list_of_ints_invalid1():
        return (1, 2, 3)

    @decorator
    def list_of_ints_invalid2():
        return [1, 2, "3"]

    assert list_of_ints_valid() == [1, 2, 3]
    pytest.raises(ReturnTypeError, list_of_ints_invalid1)
    pytest.raises(ReturnTypeError, list_of_ints_invalid2)


def test_typed_return_with_compound_of_compound_types():
    decorator = typed_return([[int]])

    @decorator
    def list_of_list_of_ints_valid():
        return [[1], [2], [3]]

    @decorator
    def list_of_list_of_ints_invalid1():
        return ([1], [2], [3])

    @decorator
    def list_of_list_of_ints_invalid2():
        return [[1], [2], ["3"]]

    assert list_of_list_of_ints_valid() == [[1], [2], [3]]
    pytest.raises(ReturnTypeError, list_of_list_of_ints_invalid1)
    pytest.raises(ReturnTypeError, list_of_list_of_ints_invalid2)


def test_typed_return_with_combination():
    decorator = typed_return(int, lambda x: x > 0)

    @decorator
    def valid1():
        return 10

    @decorator
    def invalid1():
        return -1

    assert valid1() == 10
    pytest.raises(ReturnTypeError, invalid1)


def test_typed_return_with_dict_and_extra():
    decorator = typed_return({"a": lambda x: x > 0, "b": [str]})

    @decorator
    def valid1():
        return {"a": 1, "b": ['s']}

    @decorator
    def invalid1():
        return {"a": ['s'], "b": 1}

    @decorator
    def invalid2():
        return {}

    @decorator
    def invalid3():
        return {"a": 0, "b": ['s']}

    assert valid1() == {"a": 1, "b": ['s']}
    pytest.raises(ReturnTypeError, invalid1)
    pytest.raises(ReturnTypeError, invalid2)
    pytest.raises(ReturnTypeError, invalid3)


def test_typed_return_with_covariant_list():
    decorator = typed_return([Any])

    @decorator
    def valid1():
        return [[1], [2], [3]]

    @decorator
    def valid2():
        return ['a', 'b', 'c']

    @decorator
    def valid3():
        return [1, 2, 3]

    assert valid1() == [[1], [2], [3]]
    assert valid2() == ['a', 'b', 'c']
    assert valid3() == [1, 2, 3]


def test_typed_return_with_covariant_tuple():
    decorator = typed_return((Any,))

    @decorator
    def valid1():
        return ([1],)

    @decorator
    def valid2():
        return ('a',)

    @decorator
    def valid3():
        return (1,)

    @decorator
    def invalid1():
        return tuple()

    @decorator
    def invalid2():
        return [1]

    assert valid1() == ([1],)
    assert valid2() == ('a',)
    assert valid3() == (1,)

    pytest.raises(ReturnTypeError, invalid1)
    pytest.raises(ReturnTypeError, invalid2)


def test_typed_return_with_single_element_tuple():
    decorator = typed_return((int,))

    @decorator
    def valid1():
        return (1,)

    @decorator
    def invalid1():
        return (1, 2)

    @decorator
    def invalid2():
        return ('a',)

    valid1()
    pytest.raises(ReturnTypeError, invalid1)
    pytest.raises(ReturnTypeError, invalid2)


def test_typed_return_with_covariant_dict():
    decorator = typed_return(dict)

    @decorator
    def valid1():
        return {"a": 1}

    @decorator
    def valid2():
        return {"a": 's'}

    @decorator
    def valid3():
        return {}

    valid1()
    valid2()
    valid3()


def test_typed_return_with_complex_list_type():
    decorator = typed_return(
        [(str, int)]
    )

    @decorator
    def valid1():
        return [('a', 1), ('b', 2)]

    @decorator
    def valid2():
        return []

    @decorator
    def invalid1():
        return [1, 2, 3]

    @decorator
    def invalid2():
        return ['a', 1, 'b']

    valid1()
    valid2()
    pytest.raises(ReturnTypeError, invalid1)
    pytest.raises(ReturnTypeError, invalid2)


def test_typed_return_with_exclusive_dict():
    decorator = typed_return({"a": int})

    @decorator
    def valid1():
        return {"a": 1}

    @decorator
    def invalid1():
        return {"a": 1, "b": 2}

    valid1()
    pytest.raises(ReturnTypeError, invalid1)


def test_typed_return_with_inclusive_dict():
    decorator = typed_return({"a": str, Any: int})

    @decorator
    def valid1():
        return {"a": "s", "b": 1}

    @decorator
    def invalid1():
        return {"a": "s", "b": "s"}

    valid1()
    pytest.raises(ReturnTypeError, invalid1)


def test_typed_return_with_literal_sets():
    decorator = typed_return({str})

    @decorator
    def valid1():
        return {"a", "b"}

    @decorator
    def invalid1():
        return {"a", 1.0}

    valid1()
    pytest.raises(ReturnTypeError, invalid1)


def test_min_length():
    decorator = typed_return(str, MinLength(10))

    @decorator
    def valid1():
        return 'a' * 11

    @decorator
    def invalid1():
        return 'a'

    valid1()
    pytest.raises(ReturnTypeError, invalid1)


def test_multiple_types():
    decorator = typed_return(str, MinLength(10), Contains('c'))

    @decorator
    def valid1():
        return 'a' * 11 + 'c'

    @decorator
    def invalid1():
        return 'a' * 11

    @decorator
    def invalid2():
        return 'a'

    valid1()
    pytest.raises(ReturnTypeError, invalid1)
    pytest.raises(ReturnTypeError, invalid2)


def test_range():
    decorator = typed_return(basestring, Range(1, 5))

    @decorator
    def valid1():
        return 'a'

    @decorator
    def valid2():
        return 'abcde'

    @decorator
    def invalid1():
        return ''

    @decorator
    def invalid2():
        return 'abcdef'

    valid1()
    valid2()
    pytest.raises(ReturnTypeError, invalid1)
    pytest.raises(ReturnTypeError, invalid2)


def test_regexp():
    decorator = typed_return(basestring, RegExpPattern("abc"))

    @decorator
    def valid1():
        return 'xx abc yy'

    @decorator
    def invalid1():
        return 'xaby'
    valid1()
    pytest.raises(ReturnTypeError, invalid1)
