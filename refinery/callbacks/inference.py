import pandas as pd
from refinery import exceptions


class ModelCallback:
    def __init__(
        self, client, inference_fn, preprocessing_fn=None, postprocessing_fn=None
    ):
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

            yield {"index": batched_indices, "associations": batched_outputs}
