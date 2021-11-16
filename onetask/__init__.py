# -*- coding: utf-8 -*-

from typing import Callable, Optional
from wasabi import msg
import pandas as pd
import numpy as np
from tqdm import tqdm
import json
from onetask import api_calls, settings, util, auto_lf, embedding
import numpy as np
from bertopic import BERTopic
from collections import defaultdict


class Client:
    def __init__(
        self, user_name: str, password: str, project_id: str, stage: str = "beta"
    ):
        settings.set_stage(stage)
        self.session_token = api_calls.create_session_token(
            user_name=user_name, password=password
        )
        self.project_id = project_id
        if self.session_token is not None:
            msg.good("Logged in to system.")
            if not api_calls.GetProjectExists(project_id, self.session_token).exists:
                msg.fail(f"Project with ID {self.project_id} does not exist.")
        else:
            msg.fail("Could not log in. Please check your username and password.")

    def _get_unique_attributes(self):
        attributes = api_calls.GetUniqueAttributes(
            self.project_id, self.session_token
        ).attributes
        return attributes

    def register_lf(self, lf: Callable, autoexecute: bool = True) -> None:
        project_id, name, source_code, docs = util.unpack_python_function(
            lf, self.project_id
        )
        if api_calls.PostLabelingFunction(
            project_id, name, source_code, docs, autoexecute, self.session_token
        ).already_exists:
            msg.warn(
                f"Labeling function '{name}' already exists. It has not been entered again!"
            )
        else:
            msg.good(f"Registered labeling function '{name}'.")

    def get_records(self, manually_labeled=True) -> pd.DataFrame:
        records = api_calls.GetRecords(
            self.project_id, self.session_token, manually_labeled=manually_labeled
        ).records

        fetched_df = pd.DataFrame(records)
        if len(fetched_df) > 0:
            df = fetched_df["data"].apply(pd.Series)
            df["label"] = fetched_df["label"]
            return df
        else:
            msg.warn("Empty result")
            return fetched_df  # empty df

    def get_embeddings(self, config_string):
        embeddings = api_calls.GetEmbeddings(
            self.project_id, self.session_token, config_string
        ).embeddings

        fetched_embeddings = pd.DataFrame(embeddings)
        if len(fetched_embeddings) > 0:
            df = fetched_embeddings["data"].apply(pd.Series)
            df[config_string] = fetched_embeddings["embedding"]
            return df
        else:
            msg.warn("Empty result")
            return fetched_embeddings

    def generate_embeddings(self, attribute_configs_dict, file_path=None):
        if not file_path:
            file_path = f"embeddings_{self.project_id}.json"

        msg.info("Loading schema")
        attributes = self._get_unique_attributes()
        unique_attribute = None
        for attr in attributes:
            if attr["unique"]:
                unique_attribute = attr["name"]

        embedding_name = "-".join(list(attribute_configs_dict.values()))

        if unique_attribute:
            msg.info("Loading records")
            records = self.get_records(manually_labeled=False)
            embedding_concat = defaultdict(list)
            for attribute, config_string in attribute_configs_dict.items():
                vals = np.stack(records[attribute])
                records_subset = records[[unique_attribute, attribute]].to_dict(
                    orient="records"
                )
                msg.info(f"Loading embedding model {config_string} for {attribute}")
                model = embedding.get_fitted_model_by_config_string(config_string, vals)
                if model:
                    msg.info("Starting embedding procedure")
                    for idx, row in tqdm(
                        enumerate(records_subset),
                        total=len(records_subset),
                        desc="Embedding records...",
                    ):
                        embedding_concat[idx].extend(
                            model.encode(row[attribute]).tolist()
                        )
            msg.good(f"Finished embedding procedure. Storing to {file_path}")
            export = []
            for unique_val, embedding_vector in embedding_concat.items():
                export.append(
                    {unique_attribute: unique_val, embedding_name: embedding_vector}
                )
            with open(file_path, "w") as file:
                json.dump(export, file)
        else:
            msg.fail(
                "Currently, you must have exactly one unique attribute for embedding generation. Please validate this in the web app under 'Settings'"
            )

    def model_topics(self, attribute, config_string):
        msg.info("Loading embeddings")
        embeddings_df = self.get_embeddings(config_string)
        if len(embeddings_df) > 0:
            docs = embeddings_df[attribute].tolist()
            embeddings = np.stack(embeddings_df[config_string])

            msg.info("Fitting Topic Model")
            model = BERTopic(verbose=True, n_gram_range=[1, 2], top_n_words=30)
            model.fit(docs, embeddings)
            msg.good("Finished training")
            msg.info(
                "Further docs: https://maartengr.github.io/BERTopic/tutorial/visualization/visualization.html"
            )
            return model

    def generate_regex_labeling_functions(
        self, nlp, attribute, min_precision=0.8, filter_stopwords=False
    ):
        records = self.get_records()
        if len(records) > 0:
            candidates = auto_lf.derive_regex_candidates(
                nlp, records, attribute, filter_stopwords
            )
            return auto_lf.create_regex_fns(
                records, candidates, attribute, min_precision
            )
        else:
            msg.fail("No manually labeled records available!")

    def display_generated_labeling_functions(
        self, lf_df: pd.DataFrame, label: Optional[str] = None
    ):
        if label is not None:
            lf_df = lf_df.loc[lf_df["label"] == label]
        for _, row in lf_df.iterrows():
            est_coverage = row["est_coverage"]
            est_precision = row["est_precision"]
            code = row["code"]
            msg.info(
                f"Coverage: {est_coverage * 100}% | Precision: {est_precision * 100}%"
            )
            print(code)
            print()
