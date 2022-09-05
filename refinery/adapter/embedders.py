from embedders.classification.contextual import TransformerSentenceEmbedder
from refinery.adapter.util import split_train_test_on_weak_supervision


def build_classification_dataset(
    client, sentence_input, classification_label, config_string
):
    embedder = TransformerSentenceEmbedder(config_string)

    manual_data, weakly_supervised_data, labels = split_train_test_on_weak_supervision(
        client, sentence_input, classification_label
    )

    weakly_supervised_data = weakly_supervised_data.head(100)

    embeddings_test = embedder.transform(manual_data[sentence_input].tolist())
    embeddings_train = embedder.transform(
        weakly_supervised_data[sentence_input].tolist()
    )

    return {
        "train": {
            "inputs": embeddings_train,
            "labels": weakly_supervised_data["label"],
        },
        "test": {"inputs": embeddings_test, "labels": manual_data["label"]},
    }
