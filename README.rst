relaxed_types
=============

This library provides a DSL to do type check in Python. The following is provided:

* ``typed_return``: Decorator used to verify the type of the return value
* ``check_type``: Checks if a value matches to type and predicate specifications
* ``Any``: A sentinel object that matches any python object used with ``check_type`` or ``typed_returned``
* ``ReturnTypeError``: The exception that ``check_type`` raises if a type check fails



The main goal of this library is to have a simple way to ensure return types dynamically via ``typed_return``.


typed_return
------------



Lists
+++++

The following snippet shows how to perform a type check (list of integers):

.. code:: python


    >>> @typed_return([int])
    ... def func(v):
    ...     return v + [3, 4]
    ...
    >>> func([1, 2])
    [1, 2, 3, 4]
    >>> func([1, 2.0])
    Traceback (most recent call last):
      ...
    relaxed_types.ReturnTypeError: Type mismatch for 2.0, expected <type 'int'>. Outer value: [1, 2.0, 3, 4]


Tuples
++++++


Different from lists, tuples have a fixed size. The tuple specification length has to match the value length.


.. code:: python

    >>> @typed_return( (str, int) )
    ... def func(v):
    ...     return v
    ...
    >>> func( ('hello', 123) )
    ('hello', 123)
    >>> func( ('hello', 'world') )
    Traceback (most recent call last):
      ...
    relaxed_types.ReturnTypeError: Type mismatch for 'world', expected <type 'int'>. Outer value: ('hello', 'world')


Sets
++++

Sets behave the same as lists:


.. code:: python

    >>> @typed_return({str})
    ... def func(x):
    ...     return x.union({"test"})
    ...
    >>> func({"a", "b"})
    set(['a', 'test', 'b'])
    >>> func({"a", "b", 1, 2, 3})
    Traceback (most recent call last):
      ...
    relaxed_types.ReturnTypeError: Type mismatch for 1, expected <type 'str'>. Outer value: set(['a', 1, 2, 3, 'test', 'b'])


Dictionaries
++++++++++++

It is possible to specify the expected types for dictionary key values. All keys specified must exist in the dictionary —- the value ``Any`` can be specified as a key in order to validate additional keys.


.. code:: python

    >>> @typed_return({"name": str, "age": int})
    ... def func(v):
    ...     v['test'] = 'test'
    ...     return v
    ...
    >>> func({"name": "John Doe", "age": 21})
    {'test': 'test', 'age': 21, 'name': 'John Doe'}
    >>> func({"name": "Guy", "age": "47"})
    Traceback (most recent call last):
      ...
    relaxed_types.ReturnTypeError: Type mismatch for '47', expected <type 'int'>. Outer value: {'test': 'test', 'age': '47', 'name': 'Guy'}



The following example shows how to specify a dictionary with key ``name`` as ``str`` and any other key as ``int``.

.. code:: python

    >>> from relaxed_types import *
    >>> @typed_return({"name": str, Any: int})
    ... def func(x):
    ...     return x
    ...
    >>> func({"name": "John Doe", "b": 2, "c": 3})
    {"name": "John Doe", "b": 2, "c": 3}



Predicates
++++++++++

Predicates allow you to create custom type checks.
A predicate is a function that expects an object and returns a boolean: ``True`` means the object passed in matches the expectations and ``False`` means it does not.

The following snippet ensures `func` only returns odd numbers:

.. code:: python

    >>> def odd(x):
    ...     return x % 2 != 0
    ...
    >>> @typed_return(odd)
    ... def func(v):
    ...     return v * 3
    ...
    >>> func(1)
    3
    >>> func(2)
    Traceback (most recent call last):
      ...
    relaxed_types.ReturnTypeError: Type mismatch for 6, expected <function odd at ...>. Outer value: 6


Because of predicate support, you can integrate ``relaxed_types`` with other libraries, such as voluptuous_:

.. code:: python

    >>> from voluptuous import Length
    >>> @typed_return([int], Length(min=10, max=100))
    ... def func(l):
    ...     return l * 2
    ...
    >>> func(range(10))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> func(range(3))
    Traceback (most recent call last):
      ...
    voluptuous.LengthInvalid: length of value must be at least 10

The only issue with this integration is that it might either raise ``ReturnTypeError`` or
an exception that inherits from ``voluptuous.errors.Invalid``.



Combining all together
++++++++++++++++++++++

It's possible to combine lists, tuples, dictionaries, predicates, and any Python type.

.. code:: python

    >>> @typed_return(int, lambda x: x > 0)
    ... def func1(x):
    ...     return x + 10
    ...
    >>>
    >>> func1(10)
    20
    >>> func1(-100)
    Traceback (most recent call last):
      ...
    relaxed_types.ReturnTypeError: Type mismatch for -90, expected <type 'int'>. Outer value: -90



    >>> @typed_return([int], lambda x: len(x) > 0)
    ... def func1(x):
    ...     return x
    ...
    >>>
    >>> func1([1, 2])
    [1, 2]
    >>> func1([])
    Traceback (most recent call last):
      ...
    relaxed_types.ReturnTypeError: Type mismatch for [], expected [<type 'int'>]. Outer value: []


    >>> @typed_return([ {"name": lambda x: x.upper() == x} ])
    ... def func2(x):
    ...     return x
    ...
    >>>
    >>> func2([{"name": "JOHN DOE"}])
    [{'name': 'JOHN DOE'}]
    >>> func2([{"name": "test"}])
    Traceback (most recent call last):
      ...
    relaxed_types.ReturnTypeError: Type mismatch for 'test', expected <function <lambda> at 0x10e325758>. Outer value: [{'name': 'test'}]


    >>> @typed_return([{"data": Any, "id": lambda x: isinstance(x, int) and x > 0}])
    ... def func3(x):
    ...     return x
    ...
    >>> func3([{"data": "price=10", "id": 1}])
    [{'data': 'price=10', 'id': 1}]
    >>> func3([{"data": 10, "id": 2}])
    [{'data': 10, 'id': 2}]
    >>> func3([{"data": {"price": 10}, "id": 2}])
    [{'data': {'price': 10}, 'id': 2}]


.. _voluptuous: https://github.com/alecthomas/voluptuous