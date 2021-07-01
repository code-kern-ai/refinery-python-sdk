# -*- coding: utf-8 -*-
import pkg_resources

from onetask import exceptions, settings

try:
    version = pkg_resources.get_distribution("onetask").version
except pkg_resources.DistributionNotFound:
    version = "noversion"

import requests
from typing import Dict, Any, Optional, Union

from better_abc import ABCMeta, abstract_attribute


class OneTaskCall(metaclass=ABCMeta):

    def __init__(
            self,
            url: str,
            api_token: str,
            data: Optional[Dict[str, Any]] = None
    ):

        url = url
        headers = {
            # "Authorization": f"Token {api_token}",
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
    def content(self) -> Union[Dict[str, Any], exceptions.APIError]:
        status_code = self.response.status_code

        json_data = self.response.json()
        if status_code == 200:
            return json_data
        else:
            error_code = json_data.get("error_code")
            error_message = json_data.get("error_message")
            exception = exceptions.get_api_exception_class(
                status_code=status_code,
                error_code=error_code,
                error_message=error_message
            )
            raise exception


class PostCall(OneTaskCall):

    def __init__(
            self,
            url: str,
            # api_token: str, TODO: include once auth is done
            data: Dict[str, Any],
    ):
        self.method = "POST"

        api_token = ""
        super().__init__(
            url=url,
            api_token=api_token,
            data=data
        )


class RegisterLabelingFunctionCall(PostCall):

    def __init__(
            self,
            fn_name: str,
            source_code: str,
            description: str,
            org_id: str,
            project_id: str,
    ):
        body = {
            "org_id": org_id,
            "project_id": project_id,
            "name": fn_name,
            "function": source_code,
            "description": description
        }
        super().__init__(
            url=settings.LABELING_FUNCTION_URL,
            data=body
        )
