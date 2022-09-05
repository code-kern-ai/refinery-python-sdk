import os
from refinery import Client
from refinery.adapter.util import split_train_test_on_weak_supervision
from datasets import load_dataset


def build_classification_dataset(
    client: Client, sentence_input: str, classification_label: str
):
    """Build a classification dataset from a refinery client and a config string useable for HuggingFace finetuning.

    Args:
        client (Client): Refinery client
        sentence_input (str): Name of the column containing the sentence input.
        classification_label (str): Name of the label; if this is a task on the full record, enter the string with as "__<label>". Else, input it as "<attribute>__<label>".

    Returns:
        _type_: HuggingFace dataset
    """

    df_train, df_test, label_options = split_train_test_on_weak_supervision(
        client, sentence_input, classification_label
    )

    mapping = {k: v for v, k in enumerate(label_options)}

    df_train["label"] = df_train["label"].apply(lambda x: mapping[x])
    df_test["label"] = df_test["label"].apply(lambda x: mapping[x])

    hash_val = hash(str(client.project_id))
    train_file_path = f"{hash_val}_train_file.csv"
    test_file_path = f"{hash_val}_test_file.csv"

    df_train.to_csv(train_file_path, index=False)
    df_test.to_csv(test_file_path, index=False)

    dataset = load_dataset(
        "csv", data_files={"train": train_file_path, "test": test_file_path}
    )

    if os.path.exists(train_file_path):
        os.remove(train_file_path)

    if os.path.exists(test_file_path):
        os.remove(test_file_path)

    return dataset, mapping
