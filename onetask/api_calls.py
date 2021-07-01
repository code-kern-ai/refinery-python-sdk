# -*- coding: utf-8 -*-
import pkg_resources

try:
    version = pkg_resources.get_distribution("onetask").version
except pkg_resources.DistributionNotFound:
    version = "noversion"

import requests
from typing import Dict, Any, Optional, Union

from better_abc import ABCMeta, abstract_attribute



class OneTaskCall(metaclass=ABCMeta):
    """
    Base entity for calls to the onetask SDK API.

    :param url: URL of the API to be addressed.
    :param api_token: Your API token provided in the client.
    :param params: Request parameters.
    :param data: Request data.
    """

    def __init__(
            self,
            url: str,
            org_id: str,
            project_id: str,
            data: Optional[Dict[str, Any]] = None
    ):

        url = url
        headers = {
            #"Authorization": f"Token {api_token}",
            "Content-Type": "application/json",
            "User-Agent": f"python-sdk-{version}"
        }
        if data is None:
            self.response = requests.request(self.method, url, headers=headers)
        else:
            self.response = requests.request(self.method, url, json=data, headers=headers)

    @abstract_attribute
    def method(self):
        pass

    @property
    def content(self) -> Union[Dict[str, Any], exceptions.OneTaskError]:
        """
        Contains the result of the request.

        :raise: OneTaskError if the SDK has not been used correctly.
        :return: Request response data.
        """
        status_code = self.response.status_code

        json_data = self.response.json()
        if status_code == 200:
            return json_data
        else:
            error_code = json_data.get("error_code")
            error_message = json_data.get("error_message")
            exception = exceptions.get_exception_class(
                status_code=status_code,
                error_code=error_code,
                error_message=error_message
            )
            raise exception


class GetCall(OneTaskCall):
    """
    Base entity for GET calls to the onetask SDK API.

    :param url: URL of the API to be addressed.
    :param api_token: Your API token provided in the client.
    :param project_id: Request data.
    :param params: Request parameters.
    """

    def __init__(
            self,
            url: str,
            api_token: str,
            project_id: str,
            params: Dict[str, Any]
    ):
        self.method = "GET"

        params = {
            "project_id": project_id,
            **params
        }

        super().__init__(
            url=url,
            api_token=api_token,
            params=params
        )


class PostCall(OneTaskCall):
    """
    Base entity for POST calls to the onetask SDK API.

    :param url: URL of the API to be addressed.
    :param api_token: Your API token provided in the client.
    :param project_id: The Project ID provided to you.
    :param data: Request data.
    :param params: Request parameters.
    """

    def __init__(
            self,
            url: str,
            api_token: str,
            project_id: str,
            data: Dict[str, Any],
            params: Optional[Dict[str, Any]] = None
    ):
        self.method = "POST"

        if data is None:
            data = {"project_id": project_id}
        else:
            data = {
                "project_id": project_id,
                **data
            }

        super().__init__(
            url=url,
            api_token=api_token,
            data=data,
            params=params
        )


class GetProjectInfoCall(GetCall):
    """
    GET Call to the Project Information SDK endpoint.

    :param api_token: Your API token provided in the client.
    :param project_id: The Project ID provided to you.
    """

    def __init__(self, api_token: str, project_id: str):
        super().__init__(
            url=settings.PROJECT_INFO_URL,
            api_token=api_token,
            project_id=project_id,
            params={}
        )


class RegisterLabelingFunctionCall(PostCall):
    """
    POST Call to the Labeling Function Registry SDK endpoint.

    :param labeling_function: Labeling function that should be registered.
    :param api_token: Your API token provided in the client.
    :param project_id: The Project ID provided to you.
    """

    def __init__(
            self, labeling_function: entities.LabelingFunction, api_token: str, project_id: str
    ):
        super().__init__(
            url=settings.LF_INSTANCE_URL,
            api_token=api_token,
            project_id=project_id,
            data=dict(labeling_function)
        )
