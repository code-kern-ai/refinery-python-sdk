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


# no call to the onetask system, therefore include it here
def create_session_token(
        user_name: str,
        password: str
):
    headers = {"Accept": "application/json"}
    action_url = (
        requests.get(settings.AUTHENTICATION_URL, headers=headers)
            .json()
            .get("ui")
            .get("action")
    )
    session_token = (
        requests.post(
            action_url,
            headers=headers,
            json={"method": "password", "password": password, "password_identifier": user_name},
        )
            .json()
            .get("session_token")
    )

    return session_token


class OneTaskCall(metaclass=ABCMeta):

    def __init__(
            self,
            url: str,
            session_token: str,
            data: Optional[Dict[str, Any]] = None
    ):

        url = url
        headers = {
            "Authorization": f"Bearer {session_token}",
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
            session_token: str,
            data: Dict[str, Any],
    ):
        self.method = "POST"

        super().__init__(
            url=url,
            session_token=session_token,
            data=data
        )


class RegisterLabelingFunctionCall(PostCall):

    def __init__(
            self,
            fn_name: str,
            source_code: str,
            description: str,
            project_id: str,
            session_token: str
    ):
        body = {
            "org_id": "60db22faea4261f4df63a3b1",  # TODO: remove
            "project_id": project_id,
            "name": fn_name,
            "function": source_code,
            "description": description
        }
        super().__init__(
            url=settings.LABELING_FUNCTION_URL,
            session_token=session_token,
            data=body
        )
