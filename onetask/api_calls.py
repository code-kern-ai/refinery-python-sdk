# -*- coding: utf-8 -*-
from json.decoder import JSONDecodeError
import pkg_resources
from onetask import exceptions, settings
import requests

try:
    version = pkg_resources.get_distribution("onetask").version
except pkg_resources.DistributionNotFound:
    version = "noversion"


# no call to the onetask system, therefore include it here
def create_session_token(user_name: str, password: str):
    headers = {"Accept": "application/json"}
    action_url = (
        requests.get(settings.get_authentication_url(), headers=headers)
        .json()
        .get("ui")
        .get("action")
    )
    session_token = (
        requests.post(
            action_url,
            headers=headers,
            json={
                "method": "password",
                "password": password,
                "password_identifier": user_name,
            },
        )
        .json()
        .get("session_token")
    )

    return session_token


class PostRequest:
    def __init__(self, url, body, session_token):
        self.url = url
        self.body = body
        self.session_token = session_token

    def execute(self):

        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"python-sdk-{version}",
            "Authorization": f"Bearer {self.session_token}",
        }

        response = requests.post(url=self.url, json=self.body, headers=headers)

        status_code = response.status_code

        if status_code == 200:
            json_data = response.json()
            return json_data
        else:
            try:
                json_data = response.json()
                error_code = json_data.get("error_code")
                error_message = json_data.get("error_message")
            except JSONDecodeError:
                error_code = 500
                error_message = "The server was unable to process the provided data."

            exception = exceptions.get_api_exception_class(
                status_code=status_code,
                error_code=error_code,
                error_message=error_message,
            )
            raise exception


class PostLabelingFunction(PostRequest):
    def __init__(
        self, project_id, name, function, description, autoexecute, session_token
    ):

        body = {
            "project_id": project_id,
            "name": name,
            "function": function,
            "description": description,
            "autoexecute": autoexecute,
        }

        super().__init__(settings.get_post_lf_url(), body, session_token)
        self.already_exists = self.execute()["already_exists"]


class PostProjectExists(PostRequest):
    def __init__(self, project_id, session_token):

        body = {
            "project_id": project_id,
        }

        super().__init__(settings.get_project_exists_url(), body, session_token)
        self.exists = self.execute()["exists"]


class PostManuallyLabeledRecords(PostRequest):
    def __init__(self, project_id, session_token):

        body = {
            "project_id": project_id,
        }

        super().__init__(settings.get_manually_labeled_data_url(), body, session_token)
        self.records = self.execute()["records"]
