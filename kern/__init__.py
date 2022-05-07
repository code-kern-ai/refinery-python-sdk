# -*- coding: utf-8 -*-

from wasabi import msg
import pandas as pd
from kern import authentication, api_calls, settings, exceptions
from typing import Optional


class Client:
    """Client object which can be used to directly address the Kern AI API.

    Args:
        user_name (str): Your username for the application.
        password (str): The respective password. Do not share this!
        project_id (str): The link to your project. This can be found in the URL in an active project.
        uri (str, optional): Link to the host of the application. Defaults to "https://app.kern.ai".

    Raises:
        exceptions.get_api_exception_class: If your credentials are incorrect, an exception is raised.
    """

    def __init__(
        self, user_name: str, password: str, project_id: str, uri="https://app.kern.ai"
    ):
        settings.set_base_uri(uri)
        self.session_token = authentication.create_session_token(
            user_name=user_name, password=password
        )
        if self.session_token is not None:
            msg.good("Logged in to system.")
        else:
            msg.fail(f"Could not log in at {uri}. Please check username and password.")
            raise exceptions.get_api_exception_class(401)
        self.project_id = project_id

    def fetch_export(self, num_samples: Optional[int] = None) -> pd.DataFrame:
        """Collects the export data of your project (i.e. the same data if you would export in the web app).

        Args:
            num_samples (Optional[int], optional): If set, only the first `num_samples` records are collected. Defaults to None.

        Returns:
            pd.DataFrame: DataFrame containing your record data. For more details, see https://docs.kern.ai
        """
        url = settings.get_export_url(self.project_id, num_samples=num_samples)
        api_response = api_calls.get_request(url, self.session_token)
        df = pd.read_json(api_response)
        return df
