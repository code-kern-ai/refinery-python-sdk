from typing import List, Any, Dict
from refinery import Client
from refinery.callbacks.inference import ModelCallback
from sklearn.base import BaseEstimator


def initialize_fn(inputs, labels, **kwargs):
    return {"clf": kwargs["clf"]}


def postprocessing_fn(outputs, **kwargs):
    named_outputs = []
    for prediction in outputs:
        pred_index = prediction.argmax()
        label = kwargs["clf"].classes_[pred_index]
        confidence = prediction[pred_index]
        named_outputs.append([label, confidence])
    return named_outputs


class SklearnCallback(ModelCallback):
    def __init__(
        self,
        client: Client,
        sklearn_model: BaseEstimator,
        labeling_task_name: str,
    ) -> None:
        """Callback for sklearn models.

        Args:
            client (Client): Refinery client
            sklearn_model (BaseEstimator): Sklearn model
            labeling_task_name (str): Name of the labeling task
        """

        super().__init__(
            client,
            sklearn_model.__class__.__name__,
            labeling_task_name,
            inference_fn=sklearn_model.predict_proba,
            initialize_fn=initialize_fn,
            postprocessing_fn=postprocessing_fn,
        )
        self.sklearn_model = sklearn_model
        self.initialized = False
        self.kwargs = {"clf": self.sklearn_model}

    def run(self, inputs: List[Any], indices: List[Dict[str, Any]]) -> None:
        if not self.initialized:
            self.initialize(None, None)
            self.initialized = True
        super().run(inputs, indices)
