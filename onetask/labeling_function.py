import inspect
from typing import Callable, List

from onetask import exceptions


def unpack_python_function(fn: Callable):
    name = fn.__name__
    replace_operations = {
        f"def {name}(": "def lf(",
        f'    """{fn.__doc__}"""\n': "",
        "    ": "\t",
    }
    source_code = inspect.getsource(fn)
    for key, value in replace_operations.items():
        source_code = source_code.replace(key, value)
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


def build_keywords_lf(
    label, keywords: List[str], attributes: List[str], lowercase: bool
):
    fn_name = f"lookup_kw_{'_'.join(keywords)}_in_{'_'.join(attributes)}"
    source_code = "def lf(record):\n"
    source_code += f"\tkeywords = {keywords}\n"
    source_code += "\tattributes = ["
    for attribute in attributes:
        if lowercase:
            source_code += f"record['{attribute}'].lower(),"
        else:
            source_code += f"record['{attribute}'],"
    source_code += "]\n\tfor keyword in keywords:\n"
    source_code += "\t\tfor attribute in attributes:\n"
    source_code += "\t\t\tif keyword in attribute:\n"
    source_code += f"\t\t\t\treturn '{label}'\n"
    description = f"Lookup keywords {keywords} in attributes {attributes}"
    return fn_name, source_code, description
