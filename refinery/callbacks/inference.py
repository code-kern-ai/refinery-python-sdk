from email.generator import Generator
from typing import Any, Callable, Dict, List, Optional
import pandas as pd
from refinery import Client, exceptions


class ModelCallback:
    def __init__(
        self,
        client: Client,
        model_name: str,
        label_task_name: str,
        inference_fn: Callable,
        initialize_fn: Optional[Callable] = None,
        preprocessing_fn: Optional[Callable] = None,
        postprocessing_fn: Optional[Callable] = None,
        **kwargs
    ):
        """

        Args:
            client (Client): Refinery client
            model_name (str): Name of the model
            label_task_name (str): Name of the label task
            inference_fn (Callable): Function you want to apply for inference
            initialize_fn (Optional[Callable], optional): Function to execute to compute internal states. Defaults to None.
            preprocessing_fn (Optional[Callable], optional): Function to preprocess model inputs. Defaults to None.
            postprocessing_fn (Optional[Callable], optional): Function to postprocess model outputs. Defaults to None.
        """
        self.model_name = model_name
        self.label_task_name = label_task_name
        self.client = client
        self.inference_fn = inference_fn
        self.initialize_fn = initialize_fn
        self.preprocessing_fn = preprocessing_fn
        self.postprocessing_fn = postprocessing_fn
        self.primary_keys = client.get_primary_keys()
        self.kwargs = kwargs

    @staticmethod
    def __batch(documents: List[Any]) -> Generator:
        """Batch documents into chunks of BATCH_SIZE.

        Args:
            documents (List[Any]): List of documents

        Yields:
            Generator: Generator of batches
        """
        BATCH_SIZE = 32
        length = len(documents)
        for idx in range(0, length, BATCH_SIZE):
            yield documents[idx : min(idx + BATCH_SIZE, length)]

    def initialize(
        self, inputs: Optional[List[Any]], labels: Optional[List[Any]] = None
    ) -> None:
        """Initialize states for the computation.

        Args:
            inputs (Optional[List[Any]], optional): List of inputs. Defaults to None.
            labels (Optional[List[Any]], optional): List of labels. Defaults to None.
        """
        if self.initialize_fn:
            self.kwargs = self.initialize_fn(inputs, labels, **self.kwargs)

    def run(self, inputs: List[Any], indices: List[Dict[str, Any]]) -> None:
        """Run the pipeline and send the results to refinery.

        Args:
            inputs (List[Any]): List of inputs
            indices (List[Dict[str, Any]]): List of indices

        Raises:
            exceptions.PrimaryKeyError: If the primary key is not found in the indices
        """
        indices_df = pd.DataFrame(indices)
        if not all([key in indices_df.columns for key in self.primary_keys]):
            raise exceptions.PrimaryKeyError("Errorneous primary keys given for index.")

        index_generator = ModelCallback.__batch(indices)
        for batched_inputs in ModelCallback.__batch(inputs):
            batched_indices = next(index_generator)

            if self.preprocessing_fn is not None:
                batched_inputs = self.preprocessing_fn(batched_inputs, **self.kwargs)

            batched_outputs = self.inference_fn(batched_inputs)

            if self.postprocessing_fn is not None:
                batched_outputs = self.postprocessing_fn(batched_outputs, **self.kwargs)

            self.client.post_associations(
                batched_outputs,
                batched_indices,
                self.model_name,
                self.label_task_name,
                "model_callback",
            )

    def initialize_and_run(
        self, inputs: List[Any], indices: List[Dict[str, Any]]
    ) -> None:
        """Initialize and run the pipeline.

        Args:
            inputs (List[Any]): List of inputs
            indices (List[Dict[str, Any]]): List of indices
        """
        self.initialize(inputs)
        self.run(inputs, indices)
