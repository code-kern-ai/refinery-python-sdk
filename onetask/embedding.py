from abc import ABC, abstractmethod
from transformers import AutoTokenizer, AutoModel
import torch
import nltk
from nltk.tokenize import sent_tokenize
from wasabi import msg
from sklearn.feature_extraction.text import CountVectorizer


def get_fitted_model_by_config_string(data_type, config_string, records):
    if data_type == "str":
        if config_string == "boc":
            return BoCEmbedder(records)
        elif config_string == "bow":
            return BoWEmbedder(records)
        elif config_string == "tfidf":
            raise NotImplementedError("TFIDF is not implemented yet")
        else:
            try:
                return BERTEmbedder(records, config_string)
            except:
                msg.fail(
                    f"Embedding '{config_string}' is unknown. Please check https://onetask.readme.io/ for more information"
                )
    else:
        msg.fail(f"Currently unsupported data type {data_type} of attribute.")


class Embedder(ABC):
    def __init__(self, records):
        self.fit(records)

    @abstractmethod
    def encode(self, document):
        pass

    @abstractmethod
    def fit(self, records):
        pass


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


class BERTEmbedder(Embedder):
    def __init__(self, records, configuration_string: str = "bert-base-uncased"):
        self.tokenizer = AutoTokenizer.from_pretrained(configuration_string)
        self.model = AutoModel.from_pretrained(
            configuration_string, output_hidden_states=True
        )
        self.model.eval()
        super().__init__(records)
        nltk.download("punkt")

    def fit(self, records):
        pass

    def encode(self, document: str):
        embeddings = []
        for sentence in sent_tokenize(document):
            encoded_dict = self.tokenizer.encode_plus(
                sentence, return_tensors="pt", max_length=512, truncation=True
            )
            with torch.no_grad():
                outputs = self.model(**encoded_dict)
            embedding = self.mean_pooling(outputs, encoded_dict["attention_mask"])
            embeddings.append(embedding)
        embedding_output = torch.mean(torch.stack(embeddings), axis=0)
        return embedding_output.cpu().numpy()[0]

    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[
            0
        ]  # First element of model_output contains all token embeddings
        input_mask_expanded = (
            attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        )
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        return sum_embeddings / sum_mask
