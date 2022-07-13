# -*- coding: utf-8 -*-
import json
from json.decoder import JSONDecodeError
import pkg_resources
from refinery import exceptions
import requests
from typing import Any, Dict

try:
    version = pkg_resources.get_distribution("refinery-python").version
except pkg_resources.DistributionNotFound:
    version = "noversion"


def post_request(url: str, body: Dict[str, Any], session_token: str) -> str:
    headers = _build_headers(session_token)
    response = requests.post(url=url, json=body, headers=headers)
    return _handle_response(response)


def get_request(url: str, session_token: str, **query_params) -> str:
    headers = _build_headers(session_token)
    response = requests.get(url=url, headers=headers, params=query_params)
    return _handle_response(response)


def _build_headers(session_token: str) -> Dict[str, str]:
    return {
        "content-type": "application/json",
        "user-agent": f"python-sdk-{version}",
        "authorization": f"Bearer {session_token}",
        "identifier": session_token,
    }


def _handle_response(response: requests.Response) -> str:
    status_code = response.status_code
    if status_code == 200:
        json_data = response.json()
        if type(json_data) == str:
            json_data = json.loads(json_data)
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
