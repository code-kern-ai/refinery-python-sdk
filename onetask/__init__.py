# -*- coding: utf-8 -*-

from typing import Callable, Optional
from wasabi import msg
import pandas as pd
import numpy as np
from tqdm import tqdm
import json
from onetask import api_calls, settings, util, auto_lf, embedding


class Client:
    def __init__(
        self, user_name: str, password: str, project_id: str, stage: str = "prod"
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

    def get_attributes(self):
        attributes = api_calls.GetUniqueAttributes(
            self.project_id, self.session_token
        ).attributes
        return attributes

    def get_records(self, manually_labeled=True):
        records = api_calls.GetRecords(
            self.project_id, self.session_token, manually_labeled=manually_labeled
        ).records

        fetched_df = pd.DataFrame(records)
        if len(fetched_df) > 0:
            df = fetched_df["data"].apply(pd.Series)
            if manually_labeled:
                df["label"] = fetched_df["label"]
            return df
        else:
            return fetched_df  # empty df

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

    def generate_embeddings(self, attribute, config_string):
        msg.info("Loading schema")
        attributes = self.get_attributes()
        unique_attribute = None
        data_type = None
        for attr in attributes:
            if attr["unique"]:
                unique_attribute = attr["name"]
            if attr["name"] == attribute:
                data_type = attr["data_type"]

        if unique_attribute:
            msg.info("Loading records")
            records = self.get_records(manually_labeled=False)
            docs = np.stack(records[attribute])
            export = records[[unique_attribute, attribute]].to_dict(orient="records")
            msg.info("Loading embedding model")
            model = embedding.get_fitted_model_by_config_string(
                data_type, config_string, docs
            )
            if model:
                msg.info("Starting embedding procedure")
                for idx, row in tqdm(
                    enumerate(export), total=len(export), desc="Embedding records..."
                ):
                    row[config_string] = model.encode(row[attribute]).tolist()
                    del row[attribute]
                    export[idx] = row
                msg.good("Finished embedding procedure")
                file_path = (
                    f"embeddings_{attribute}_{config_string}_{self.project_id}.json"
                )
                with open(file_path, "w") as file:
                    json.dump(export, file)
        else:
            msg.fail(
                "Currently, you must have exactly one unique attribute for embedding generation. Please validate this in the web app under 'Settings'"
            )

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
