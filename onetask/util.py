# -*- coding: utf-8 -*-
import inspect
from typing import Callable
import re
from onetask import exceptions


def unpack_python_function(fn: Callable, project_id: str):
    def check_signature(source_code: str) -> None:
        # validate that only one parameter is given

        parameters = re.search(r"\((.*?)\):", source_code).group(1).split(",")
        if parameters == [""]:
            number_parameters = 0
        else:
            number_parameters = len(parameters)
        if number_parameters != 1:
            raise exceptions.ParameterError(
                f"{number_parameters} parameters provided. Please use exactly one."
            )

    name = fn.__name__
    replace_operations = {
        f"def {name}(": "def lf(",
        f'    """{fn.__doc__}"""\n': "",
        "    ": "\t",
    }
    source_code = inspect.getsource(fn)
    for key, value in replace_operations.items():
        source_code = source_code.replace(key, value)
    docs = inspect.getdoc(fn) or ""  # default

    check_signature(source_code)

    return project_id, name, source_code, docs
