from typing import Callable, Optional
import pandas as pd
from refinery import Client, exceptions


class ModelCallback:
    def __init__(
        self,
        model_name: str,
        label_task_name: str,
        inference_fn: Callable,
        client: Client,
        preprocessing_fn: Optional[Callable] = None,
        postprocessing_fn: Optional[Callable] = None,
    ):
        """

        Args:
            model_name (str): Name of the model (as an idenfitier in refinery)
            label_task_name (str): Name of the label task (from refinery)
            inference_fn (Callable): Function to predict the output
            client (Client): Refinery client
            preprocessing_fn (Optional[Callable], optional): Function to apply preprocessing to your inputs. Defaults to None.
            postprocessing_fn (Optional[Callable], optional): Function to apply postprocessing to the inference function's output. Defaults to None.
        """
        self.model_name = model_name
        self.label_task_name = label_task_name
        self.client = client
        self.inference_fn = inference_fn
        self.preprocessing_fn = preprocessing_fn
        self.postprocessing_fn = postprocessing_fn

        self.primary_keys = client.get_primary_keys()

    @staticmethod
    def __batch(documents):
        BATCH_SIZE = 32
        length = len(documents)
        for idx in range(0, length, BATCH_SIZE):
            yield documents[idx : min(idx + BATCH_SIZE, length)]

    def run(self, inputs, indices):
        indices_df = pd.DataFrame(indices)
        if not all([key in indices_df.columns for key in self.primary_keys]):
            raise exceptions.PrimaryKeyError("Errorneous primary keys given for index.")

        index_generator = ModelCallback.__batch(indices)
        for batched_inputs in ModelCallback.__batch(inputs):
            batched_indices = next(index_generator)

            if self.preprocessing_fn is not None:
                batched_inputs = self.preprocessing_fn(batched_inputs)

            batched_outputs = self.inference_fn(batched_inputs)

            if self.postprocessing_fn is not None:
                batched_outputs = self.postprocessing_fn(batched_outputs)

            response = self.client.post_associations(
                batched_outputs,
                batched_indices,
                self.model_name,
                self.label_task_name,
                "model_callback",
            )
