from typing import List, Any, Dict
from refinery import Client
from refinery.callbacks.inference import ModelCallback
import torch.nn as nn
from torch.utils.data import DataLoader
from sklearn import preprocessing


def initialize_fn(inputs, labels, **kwargs):
    return {"encoder": kwargs["encoder"]}


def postprocessing_fn(outputs, **kwargs):
    named_outputs = []
    pred_argindices = outputs.argmax(axis=1)
    for predindex, pred_argindex in enumerate(pred_argindices):
        label = kwargs["encoder"].classes_[pred_argindex]
        confidence = outputs[predindex][pred_argindex].tolist()
        named_outputs.append([label, confidence])
    return named_outputs


class TorchCallback(ModelCallback):
    def __init__(
        self,
        client: Client,
        torch_model: nn.Module,
        labeling_task_name: str,
        encoder: preprocessing.LabelEncoder,
    ) -> None:
        """Callback for sklearn models.

        Args:
            client (Client): Refinery client
            sklearn_model (BaseEstimator): Sklearn model
            labeling_task_name (str): Name of the labeling task
        """

        super().__init__(
            client,
            torch_model.__class__.__name__,
            labeling_task_name,
            inference_fn=torch_model.forward,
            initialize_fn=initialize_fn,
            postprocessing_fn=postprocessing_fn,
        )
        self.torch_model = torch_model
        self.initialized = False
        self.kwargs = {"encoder": encoder}

    def run(self, loader: DataLoader, indices: List[Dict[str, Any]]) -> None:
        if not self.initialized:
            self.initialize(None, None)
            self.initialized = True
        super().run(loader.dataset.X, indices)
