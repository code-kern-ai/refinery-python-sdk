from typing import Any, Dict, Optional
from embedders.classification.contextual import TransformerSentenceEmbedder
from refinery import Client
from refinery.adapter.util import split_train_test_on_weak_supervision


def build_classification_dataset(
    client: Client,
    sentence_input: str,
    classification_label: str,
    config_string: Optional[str] = None,
    num_train: Optional[int] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Builds a classification dataset from a refinery client and a config string.

    Args:
        client (Client): Refinery client
        sentence_input (str): Name of the column containing the sentence input.
        classification_label (str): Name of the label; if this is a task on the full record, enter the string with as "__<label>". Else, input it as "<attribute>__<label>".
        config_string (Optional[str], optional): Config string for the TransformerSentenceEmbedder. Defaults to None; if None is provided, the text will not be embedded.
        num_train (Optional[int], optional): Number of training examples to use. Defaults to None; if None is provided, all examples will be used.

    Returns:
        Dict[str, Dict[str, Any]]: Containing the train and test datasets, with embedded inputs.
    """

    df_train, df_test, _, primary_keys = split_train_test_on_weak_supervision(
        client, sentence_input, classification_label, num_train
    )

    if config_string is not None:
        embedder = TransformerSentenceEmbedder(config_string)
        inputs_train = embedder.transform(df_train[sentence_input].tolist())
        inputs_test = embedder.transform(df_test[sentence_input].tolist())
    else:
        inputs_train = df_train[sentence_input].tolist()
        inputs_test = df_test[sentence_input].tolist()

    return {
        "train": {
            "inputs": inputs_train,
            "index": df_train[primary_keys].to_dict("records"),
            "labels": df_train["label"],
        },
        "test": {
            "inputs": inputs_test,
            "index": df_test[primary_keys].to_dict("records"),
            "labels": df_test["label"],
        },
    }
