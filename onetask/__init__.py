# -*- coding: utf-8 -*-
import __future__

from onetask import api_calls
from typing import Callable


class Client:
    """
    Python Client for the onetask API to register labeling functions programmatically.

    :param api_token: The API token provided to you.
    :param project_id: The Project ID provided to you.
    :param logging_file: Name of the log file to which event informations are stored.
    """

    def __init__(
            self, org_id: str, project_id: str
    ):
        self.org_id = org_id
        self.project_id = project_id

    def get_records(
            self, max_number_samples: int = None
    ):
        raise NotImplementedError

    def register_lf(
            self,
            lf: Callable
    ) -> None:
        """
        Register a onetask labeling function to your project.

        :param lf: onetask labeling function entity
        """

        call = api_calls.RegisterLabelingFunctionCall(
            labeling_function=lf,
            org_id=self.org_id,
            project_id=self.project_id
        )
