import inspect
from typing import Callable

from onetask import exceptions


def unpack_python_function(fn: Callable):
    name = fn.__name__
    source_code = inspect.getsource(fn).replace(f"def {name}(", "def lf(")
    docs = inspect.getdoc(fn)

    check_signature(source_code)

    return name, source_code, docs


def check_signature(source_code: str) -> None:
    # validate that only one parameter is given
    import re

    parameters = re.search(r"\((.*?)\):", source_code).group(1).split(",")
    if parameters == [""]:
        number_parameters = 0
    else:
        number_parameters = len(parameters)
    if number_parameters != 1:
        raise exceptions.ParameterError(
            f"{number_parameters} parameters provided. Please use exactly one."
        )
