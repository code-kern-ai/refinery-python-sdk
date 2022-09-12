from typing import List, Any, Dict
from refinery import Client
from refinery.callbacks.inference import ModelCallback
from transformers import pipeline


def initialize_fn(inputs, labels, **kwargs):
    return {"mapping": kwargs["mapping"]}


def postprocessing_fn(outputs, **kwargs):
    named_outputs = []
    for prediction in outputs:
        label = kwargs["mapping"][prediction["label"]]
        confidence = prediction["score"]
        named_output = [label, confidence]
        named_outputs.append(named_output)
    return named_outputs


class TransformerCallback(ModelCallback):
    def __init__(
        self,
        client: Client,
        transformer_model: pipeline,
        labeling_task_name: str,
        mapping: Dict[str, str],
    ) -> None:
        """Callback for sklearn models.

        Args:
            client (Client): Refinery client
            sklearn_model (BaseEstimator): Sklearn model
            labeling_task_name (str): Name of the labeling task
        """

        super().__init__(
            client,
            transformer_model.__class__.__name__,
            labeling_task_name,
            inference_fn=transformer_model.__call__,
            initialize_fn=initialize_fn,
            postprocessing_fn=postprocessing_fn,
        )
        self.sklearn_model = transformer_model
        self.initialized = False
        self.kwargs = {"mapping": mapping}

    def run(self, inputs: List[Any], indices: List[Dict[str, Any]]) -> None:
        if not self.initialized:
            self.initialize(None, None)
            self.initialized = True
        super().run(inputs, indices)
