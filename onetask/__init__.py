# -*- coding: utf-8 -*-
import logging
from typing import List, Union

import pandas as pd

from onetask import api_calls
from onetask import entities
from onetask import exceptions
from onetask import factory
from onetask import sdk_instructions
from onetask import settings
from onetask.factory import build_lf  # shortcut for convenience
from onetask.utils import object_utils
from onetask.utils.pandas_utils import attributes_df_from_records  # shortcut for convenience


class Client:
    """
    Python Client for the onetask API to register labeling functions programmatically.

    :param api_token: The API token provided to you.
    :param project_id: The Project ID provided to you.
    :param logging_file: Name of the log file to which event informations are stored.
    """

    def __init__(
            self, api_token: str, project_id: str, logging_file: str = "events.log"
    ):
        self.api_token = api_token
        self.project_id = project_id  # TODO: decide whether to include or not
        self.logging_file = logging_file
        logging.basicConfig(
            filename=logging_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p'
        )

    def __repr__(self) -> str:

        call = api_calls.GetProjectInfoCall(
            api_token=self.api_token,
            project_id=self.project_id
        )
        info_dict = call.content

        labels = [label_dict["name"] for label_dict in info_dict["labels"]]
        attributes = [label_dict["path"] for label_dict in info_dict["attributes"]]
        # embeddings = info_dict["embeddings"] # TODO: integrate once embeddings are part of the SDK
        replacement_dict = {
            "<label-list>": "".join([f" * '{label}'\n" for label in labels]),
            "<attributes-list>": "".join([f" * '{attribute}'\n" for attribute in attributes]),
            # "<embeddings-list>": "".join([f" * '{embedding}'\n" for embedding in embeddings]),
            "<attribute>": f"'{attributes[0]}'",
            "<label>": f"'{labels[0]}'"
        }
        signature_text = sdk_instructions.INSTRUCTIONS
        for token, replacement in replacement_dict.items():
            signature_text = signature_text.replace(token, replacement)
        return signature_text

    def get_all_lfs(self) -> List[entities.LabelingFunction]:
        """
        Retrieve all labeling functions stored in your current project.

        :return: List of all labeling functions as onetask entities.
        """

        call = api_calls.GetAllLabelingFunctionsCall(
            api_token=self.api_token,
            project_id=self.project_id
        )
        lf_dict_list = call.content
        lf_list = []
        for lf_dict in lf_dict_list:
            lf = factory.build_lf_from_dict(lf_dict)
            lf_list.append(lf)
        return lf_list

    def print_all_lfs(self) -> None:
        """
        Prints all registered labeling functions as python functions.
        """
        for lf in self.get_all_lfs():
            print(lf)

    def get_lf_by_id(
            self, internal_id: str
    ) -> entities.LabelingFunction:
        """
        Retrieve one specified labeling function stored in your current project using its internal custom_id.

        :param internal_id: Technical identification of the labeling function.
        :return: Labeling function as a onetask entity.
        """

        call = api_calls.GetLabelingFunctionByIdCall(
            internal_id=internal_id,
            api_token=self.api_token,
            project_id=self.project_id
        )
        lf_dict = call.content
        lf = factory.build_lf_from_dict(lf_dict)
        return lf

    def get_sample_records(
            self, max_number_samples: int = 100, as_df: bool = False
    ) -> Union[List[entities.Record], pd.DataFrame]:
        """
        Retrieve random record samples of your current project.

        :param max_number_samples: A max number of samples you want to retrieve.
        :param as_df: If true, the records are wrapped by a pandas DataFrame.
        :return: List of sample records as onetask entities.
        """

        call = api_calls.GetSampleRecordsCall(
            max_number_samples=max_number_samples,
            api_token=self.api_token,
            project_id=self.project_id
        )
        record_dict_list = call.content
        record_list = []
        for record_dict in record_dict_list:
            record = factory.build_record_from_dict(record_dict)
            record_list.append(record)
        if as_df:
            return attributes_df_from_records(record_list=record_list)
        else:
            return record_list

    def get_record_by_id(
            self, custom_id: str
    ) -> entities.Record:
        """
        Retrieve one specified record by its custom id provided at import.

        :param custom_id: Identifier of the record.
        :return: Record as a onetask entity.
        """

        call = api_calls.GetRecordByIdCall(
            custom_id=custom_id,
            api_token=self.api_token,
            project_id=self.project_id
        )
        record_dict = call.content
        record = factory.build_record_from_dict(record_dict)
        return record

    def register_lf(
            self,
            lf: entities.LabelingFunction
    ) -> None:
        """
        Register a onetask labeling function to your project.

        :param lf: onetask labeling function entity
        :raise: OneTaskError if the provided argument is not a correct labeling function.
        """

        if type(lf) != entities.LabelingFunction:
            raise exceptions.OneTaskError("Argument lf is not a onetask LabelingFunction")

        call = api_calls.RegisterLabelingFunctionCall(
            labeling_function=lf,
            api_token=self.api_token,
            project_id=self.project_id
        )
        internal_id = call.content.get("internal_id")
        lf.definition.internal_id = internal_id
