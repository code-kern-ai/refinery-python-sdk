# -*- coding: utf-8 -*-
from json.decoder import JSONDecodeError
import pkg_resources
from kern import exceptions
import requests
from typing import Any, Dict

try:
    version = pkg_resources.get_distribution("kern-python-client").version
except pkg_resources.DistributionNotFound:
    version = "noversion"


def post_request(url: str, body: Dict[str, Any], session_token: str) -> str:
    headers = _build_headers(session_token)
    response = requests.post(url=url, json=body, headers=headers)
    return _handle_response(response)


def get_request(url: str, session_token: str) -> str:
    headers = _build_headers(session_token)
    response = requests.get(url=url, headers=headers)
    return _handle_response(response)


def _build_headers(session_token: str) -> Dict[str, str]:
    return {
        "Content-Type": "application/json",
        "User-Agent": f"python-sdk-{version}",
        "Authorization": f"Bearer {session_token}",
    }


def _handle_response(response: requests.Response) -> str:
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
