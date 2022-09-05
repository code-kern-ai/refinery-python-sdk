import os
from refinery import Client
from refinery.adapter.util import get_label_names, split_train_test_on_weak_supervision
from datasets import load_dataset


def build_classification_dataset(client: Client, sentence_input, classification_label):

    manual_data, weakly_supervised_data, labels = split_train_test_on_weak_supervision(
        client, sentence_input, classification_label
    )

    label_manual, label_weakly_supervised = get_label_names(classification_label)

    mapping = {k: v for v, k in enumerate(labels)}

    manual_data["label"] = manual_data["label"].apply(lambda x: mapping[x])
    weakly_supervised_data["label"] = weakly_supervised_data["label"].apply(
        lambda x: mapping[x]
    )

    train_file_path = f"{hash(label_weakly_supervised)}_train_file.csv"
    test_file_path = f"{hash(label_manual)}_test_file.csv"

    manual_data.to_csv(test_file_path, index=False)
    weakly_supervised_data.to_csv(train_file_path, index=False)

    dataset = load_dataset(
        "csv", data_files={"train": train_file_path, "test": test_file_path}
    )

    if os.path.exists(train_file_path):
        os.remove(train_file_path)

    if os.path.exists(test_file_path):
        os.remove(test_file_path)

    return dataset, mapping
