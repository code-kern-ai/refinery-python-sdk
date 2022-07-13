# -*- coding: utf-8 -*-
from refinery import settings
import requests


def create_session_token(user_name: str, password: str) -> str:
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
