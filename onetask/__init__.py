# -*- coding: utf-8 -*-

from typing import Callable
from wasabi import msg
import pandas as pd
from onetask import api_calls, settings, util, auto_lf


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
            if not api_calls.PostProjectExists(project_id, self.session_token).exists:
                msg.fail(f"Project with ID {self.project_id} does not exist.")
        else:
            msg.fail("Could not log in. Please check your username and password.")

    def manually_labeled_records(self, as_df: bool = True):
        records = api_calls.PostManuallyLabeledRecords(
            self.project_id, self.session_token
        ).records
        if as_df and len(records) > 0:
            return pd.DataFrame(records)
        else:
            return records

    def autogenerate_regex_labeling_functions(
        self, nlp, attribute, num_functions: int = 10
    ):
        records = self.manually_labeled_records(as_df=True)
        if len(records) > 0:
            candidates = auto_lf.derive_regex_candidates(
                nlp, records, attribute, most_common=num_functions
            )
            auto_lf.create_regex_fns(records, candidates, attribute)
        else:
            msg.fail("No manually labeled records available!")

    def register_lf(self, lf: Callable) -> None:
        project_id, name, source_code, docs = util.unpack_python_function(
            lf, self.project_id
        )
        api_calls.PostLabelingFunction(
            project_id, name, source_code, docs, self.session_token
        )
        msg.good(f"Registered labeling function '{name}'.")
