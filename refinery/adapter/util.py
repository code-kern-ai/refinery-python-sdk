from typing import List, Optional, Tuple
from refinery import Client
import pandas as pd


def split_train_test_on_weak_supervision(
    client: Client, _input: str, _label: str, num_train: Optional[int] = None
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """
    Puts the data into a train (weakly supervised data) and test set (manually labeled data).
    Overlapping data is removed from the train set.

    Args:
        client (Client): Refinery client
        _input (str): Name of the column containing the sentence input.
        _label (str): Name of the label; if this is a task on the full record, enter the string with as "__<label>". Else, input it as "<attribute>__<label>".
        num_train (Optional[int], optional): Number of training examples to use. Defaults to None; if None is provided, all examples will be used.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, List[str]]: Containing the train and test dataframes and the label name options.
    """

    primary_keys = client.get_primary_keys()

    label_attribute_train = f"{_label}__WEAK_SUPERVISION"
    label_attribute_test = f"{_label}__MANUAL"

    df_test = client.get_record_export(
        tokenize=False,
        keep_attributes=primary_keys + [_input, label_attribute_test],
        dropna=True,
    ).rename(columns={label_attribute_test: "label"})

    if num_train is not None:
        num_samples = num_train + len(df_test)
    else:
        num_samples = None

    df_train = client.get_record_export(
        tokenize=False,
        keep_attributes=primary_keys + [_input, label_attribute_train],
        dropna=True,
        num_samples=num_samples,
    ).rename(columns={label_attribute_train: "label"})

    # Remove overlapping data
    df_train = df_train.drop(df_test.index.intersection(df_train.index))[:num_train]

    label_options = list(
        set(df_test.label.unique().tolist() + df_train.label.unique().tolist())
    )

    return (
        df_train.reset_index(drop=True),
        df_test.reset_index(drop=True),
        label_options,
        primary_keys,
    )
