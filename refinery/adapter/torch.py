import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn import preprocessing
from .sklearn import (
    build_classification_dataset as sklearn_build_classification_dataset,
)
from typing import Any, Dict, Optional, Tuple
from refinery import Client


class Data(Dataset):
    def __init__(self, X, y, encoder):
        # need to convert float64 to float32 else
        # will get the following error
        # RuntimeError: expected scalar type Double but found Float
        self.X = torch.FloatTensor(X)
        # need to convert float64 to Long else
        # will get the following error
        # RuntimeError: expected scalar type Long but found Float
        y_encoded = encoder.transform(y.values)
        self.y = torch.from_numpy(y_encoded).type(torch.LongTensor)
        self.len = self.X.shape[0]

    def __getitem__(self, index):
        return self.X[index], self.y[index]

    def __len__(self):
        return self.len


def build_classification_dataset(
    client: Client,
    sentence_input: str,
    classification_label: str,
    config_string: Optional[str] = None,
    num_train: Optional[int] = None,
    batch_size: Optional[int] = 32,
) -> Tuple[DataLoader, DataLoader, preprocessing.LabelEncoder]:
    """
    Builds a classification dataset from a refinery client and a config string.

    Args:
        client (Client): Refinery client
        sentence_input (str): Name of the column containing the sentence input.
        classification_label (str): Name of the label; if this is a task on the full record, enter the string with as "__<label>". Else, input it as "<attribute>__<label>".
        config_string (Optional[str], optional): Config string for the TransformerSentenceEmbedder. Defaults to None; if None is provided, the text will not be embedded.
        num_train (Optional[int], optional): Number of training examples to use. Defaults to None; if None is provided, all examples will be used.

    Returns:
        Tuple[DataLoader, DataLoader, preprocessing.LabelEncoder]: Tuple of train and test dataloaders, and the label encoder.
    """
    data = sklearn_build_classification_dataset(
        client, sentence_input, classification_label, config_string, num_train
    )

    le = preprocessing.LabelEncoder()
    le.fit(data["train"]["labels"].values)

    train_data = Data(data["train"]["inputs"], data["train"]["labels"], le)
    test_data = Data(data["test"]["inputs"], data["test"]["labels"], le)

    train_loader = DataLoader(dataset=train_data, batch_size=batch_size)
    test_loader = DataLoader(dataset=test_data, batch_size=batch_size)

    index = {"train": data["train"]["index"], "test": data["test"]["index"]}

    return train_loader, test_loader, le, index
