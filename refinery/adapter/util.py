from typing import List, Tuple
from refinery import Client
import pandas as pd


def split_train_test_on_weak_supervision(
    client: Client, _input: str, _label: str
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """
    Puts the data into a train (weakly supervised data) and test set (manually labeled data).
    Overlapping data is removed from the train set.

    Args:
        client (Client): Refinery client
        _input (str): Name of the column containing the sentence input.
        _label (str): Name of the label; if this is a task on the full record, enter the string with as "__<label>". Else, input it as "<attribute>__<label>".

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, List[str]]: Containing the train and test dataframes and the label name options.
    """

    label_attribute_train = f"{_label}__WEAK_SUPERVISION"
    label_attribute_test = f"{_label}__MANUAL"

    df_train = client.get_record_export(
        tokenize=False,
        keep_attributes=[_input, label_attribute_train],
        dropna=True,
    ).rename(columns={label_attribute_train: "label"})

    df_test = client.get_record_export(
        tokenize=False,
        keep_attributes=[_input, label_attribute_test],
        dropna=True,
    ).rename(columns={label_attribute_test: "label"})

    df_train = df_train.drop(df_test.index)

    label_options = list(
        set(df_test.label.unique().tolist() + df_train.label.unique().tolist())
    )

    return (
        df_train.reset_index(drop=True),
        df_test.reset_index(drop=True),
        label_options,
    )
