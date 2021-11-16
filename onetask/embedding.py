# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from sentence_transformers import SentenceTransformer, models
from torch import nn
import numpy as np
from wasabi import msg
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import OneHotEncoder
from transformers import logging

logging.set_verbosity_error()


def get_fitted_model_by_config_string(config_string, records):
    if config_string == "identity":
        return IdentityEmbedder(records)
    elif config_string == "boc":
        return BoCEmbedder(records)
    elif config_string == "bow":
        return BoWEmbedder(records)
    elif config_string == "onehot":
        return OneHotEmbedder(records)
    else:
        try:
            return DocumentEmbedder(records, config_string)
        except:
            msg.fail(
                f"Embedding '{config_string}' is unknown. Please check https://onetask.readme.io/ for more information"
            )


class Embedder(ABC):
    def __init__(self, records):
        self.fit(records)

    @abstractmethod
    def encode(self, document):
        pass

    @abstractmethod
    def fit(self, records):
        pass


class IdentityEmbedder(Embedder):
    def __init__(self, records):
        super().__init__(records)

    def fit(self, records):
        pass

    def encode(self, document):
        return np.array([document])


class BoCEmbedder(Embedder):
    def __init__(self, records):
        self.model = CountVectorizer(analyzer="char")
        super().__init__(records)

    def fit(self, records):
        self.model.fit(records)

    def encode(self, document):
        return self.model.transform([document]).toarray()[0]


class BoWEmbedder(Embedder):
    def __init__(self, records):
        self.model = CountVectorizer(min_df=0.1)
        super().__init__(records)

    def fit(self, records):
        self.model.fit(records)

    def encode(self, document):
        return self.model.transform([document]).toarray()[0]


class OneHotEmbedder(Embedder):
    def __init__(self, records):
        self.model = OneHotEncoder()
        super().__init__(records)

    def fit(self, records):
        self.model.fit(records.reshape(-1, 1))

    def encode(self, document):
        return self.model.transform([[document]]).toarray()[0]


class DocumentEmbedder(Embedder):
    def __init__(self, records, configuration_string: str = "distilbert-base-uncased"):
        word_embedding_model = models.Transformer(configuration_string)
        pooling_model = models.Pooling(
            word_embedding_model.get_word_embedding_dimension()
        )
        dense_model = models.Dense(
            in_features=pooling_model.get_sentence_embedding_dimension(),
            out_features=256,
            activation_function=nn.Tanh(),
        )

        self.model = SentenceTransformer(
            modules=[word_embedding_model, pooling_model, dense_model]
        )
        super().__init__(records)

    def fit(self, records):
        pass

    def encode(self, document: str):
        return self.model.encode(document)
