# -*- coding: utf-8 -*-
from typing import Any, Optional, Generator, Tuple


def create_generator(
        instance: Any
) -> Generator[Any, Tuple[str, Any], None]:
    """
    Builds a generator of a given instance.

    :param instance: Python object.
    :return: Generator yielding attributes and their values as a Tuple.
    """

    for key in instance.__dict__:
        yield key, getattr(instance, key)


def create_representational_string(
        instance: Any, indent_add: Optional[int] = 0
) -> str:
    """
    Builds a __repr__ like string of a given instance.

    :param instance: Python object.
    :param indent_add: increments the indentation of the string.
    :return: __repr__ string
    """

    base_indent = 4
    indent = base_indent + indent_add
    representational_string = f"{instance.__module__}.{instance.__class__.__name__}(\n"
    for var in vars(instance):
        val = repr(getattr(instance, var))
        representational_string += f"{' ' * indent}{var}={val},\n"
    return f"{representational_string[:-2]}\n{' ' * indent_add})"


def create_display_string(
        instance: Any
) -> str:
    """
    Builds a __str__ like string of a given instance.

    :param instance: Python object.
    :return: __str__ string
    """

    return str(dict(iter(instance)))
