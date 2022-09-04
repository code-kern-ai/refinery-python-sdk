from refinery import Client
from datasets import load_dataset
import os


def build_dataset(client: Client, sentence_input, classification_label):

    label_manual = f"{classification_label}__MANUAL"
    manual_data = client.get_record_export(
        tokenize=False, keep_attributes=[sentence_input, label_manual], dropna=True
    ).rename(columns={label_manual: "label"})

    label_weakly_supervised = f"{classification_label}__WEAK_SUPERVISION"
    weakly_supervised_data = client.get_record_export(
        tokenize=False,
        keep_attributes=[sentence_input, label_weakly_supervised],
        dropna=True,
    ).rename(columns={label_weakly_supervised: "label"})

    weakly_supervised_data = weakly_supervised_data.drop(manual_data.index)

    labels = list(
        set(
            manual_data.label.unique().tolist()
            + weakly_supervised_data.label.unique().tolist()
        )
    )

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
