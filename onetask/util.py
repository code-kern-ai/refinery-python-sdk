# -*- coding: utf-8 -*-
import inspect
from typing import Callable
import re
import json
from onetask import exceptions
import pandas as pd


def unpack_records(fetched_records):
    records = []
    fetched_records = fetched_records["data"]["searchRecords"]
    if len(fetched_records) > 0:
        for record in fetched_records:
            record_data = json.loads(record["data"])
            record_manual_labels = []
            edges = record["labelAssociations"]["edges"]
            for edge in edges:
                node = edge["node"]
                if node["source"] == "manual":
                    record_manual_labels.append(node["label"]["name"])
            records.append(
                {
                    "data": record_data,
                    "manual_labels": record_manual_labels[
                        0
                    ],  # remove [0] for multilabel support
                }
            )
        return records
    else:
        return []


def records_to_df(records):
    raw_df = pd.DataFrame(records)
    df = raw_df["data"].apply(pd.Series)
    df["label"] = raw_df["manual_labels"]
    return df


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
