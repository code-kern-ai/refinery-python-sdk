# -*- coding: utf-8 -*-

from typing import Callable, Dict, List, Optional, Union
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
    """
    Python Client for the onetask API. If you have any questions, please contact our support.

    Args:
        user_name (str): The email with which you've been registered at onetask
        password (str): Your password for onetask
        project_id (str): The unique identifier for a project, can be found in the url after projects/
        stage (str): The onetask system staging environment [beta, test, dev, local]
    """

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

    def _get_unique_attributes(self) -> List[Dict[str, Union[str, bool]]]:
        """
        Get the record schema for your project shown in the web app under 'Settings'

        Returns:
            List[Dict[str, Union[str, bool]]]: each record schema element
        """
        attributes = api_calls.GetUniqueAttributes(
            self.project_id, self.session_token
        ).attributes
        return attributes

    def register_lf(self, lf: Callable, autoexecute: bool = True) -> None:
        """
        Send a local labeling function to the onetask application. Please make sure that the function fits the desired structure (for more information, please visit onetask.readme.io/reference)

        Args:
            lf (Callable): The function object you want to send to the system
            autoexecute (bool, optional): If true, the function is automatically executed when entered in the system. Defaults to True.
        """
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

    def get_records(self, keep_unlabeled=False, keep_programmatic=False):
        """
        Get the records of your project.


        Args:
            keep_unlabeled (bool, optional): If true, you will receive all records, even if they are not labeled yet. Defaults to False.
            keep_programmatic (bool, optional): if true, you will receive also the programmatically labeled records. Defaults to False.

        Returns:
            [type]: [description]
        """
        records = api_calls.GetRecords(
            self.project_id,
            self.session_token,
            keep_unlabeled=keep_unlabeled,
            keep_programmatic=keep_programmatic,
        ).records

        fetched_df = pd.DataFrame(records)
        if len(fetched_df) > 0:
            df = fetched_df["data"].apply(pd.Series)
            df["label"] = fetched_df["label"]
            df["is_programmatic"] = fetched_df["is_programmatic"]
            return df
        else:
            msg.warn("Empty result")
            return fetched_df  # empty df

    def get_embeddings(self, config_string: str) -> pd.DataFrame:
        """
        Get the embeddings of your project of a configuration string

        Args:
            config_string (str): The name of your embedding

        Returns:
            pd.DataFrame: containing the record attributes and the embedding vectors
        """
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

    def generate_embeddings(
        self, attribute_configs_dict: Dict[str, str], file_path: Optional[str] = None
    ) -> None:
        """
        ---EXPERIMENTAL---

        Create new embeddings to upload into your project.

        Args:
            attribute_configs_dict (Dict[str, str]): describe which attribute should be embedded using which technique or model.
            file_path (Optional[str], optional): path where the embeddings should be stored to. Defaults to 'embeddings_{project_id}.json'.
        """
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
            records = self.get_records(keep_programmatic=False, keep_unlabeled=False)
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
                    for _, row in tqdm(
                        enumerate(records_subset),
                        total=len(records_subset),
                        desc="Embedding records...",
                    ):
                        embedding_concat[row[unique_attribute]].extend(
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

    def model_topics(self, attribute: str, config_string: str) -> BERTopic:
        """
        ---EXPERIMENTAL---

        Apply a BERTopic to your data to do topic modelling. Further docs: https://maartengr.github.io/BERTopic/tutorial/visualization/visualization.html

        Args:
            attribute (str): the name of the string attribute you want to model
            config_string (str): name of the embedding vector in the web application that you want to make use of. This MUST be a BERT-related embedding to work properly.

        Returns:
            BERTopic: BERTopic object that can be called for topic modelling
        """
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
        self,
        nlp,
        attribute: str,
        min_precision: Optional[float] = 0.8,
        filter_stopwords: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        ---EXPERIMENTAL---

        Autogenerate labeling functions containing regular expressions to model your data. Uses spacy to model the linguistics of your data.

        Args:
            nlp (spacy.lang): nlp object of spacy for the specific language (e.g. en_core_web_sm)
            attribute (str): the name of the attribute that should be analyzed for regular expressions
            min_precision (Optional[float], optional): needed precision to generate a labeling function. Defaults to 0.8.
            filter_stopwords (Optional[bool], optional): if set to true, stop words like 'this', 'that' etc. will be removed. Defaults to False.

        Returns:
            pd.DataFrame: [description]
        """
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
        """
        Helper function to display the autogenerated labeling functions

        Args:
            lf_df (pd.DataFrame): outcome of client.generate_regex_labeling_functions
            label (Optional[str], optional): filter option to only show one label. Defaults to None.
        """
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
