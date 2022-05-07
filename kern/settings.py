# -*- coding: utf-8 -*-
BASE_URI: str


def set_base_uri(uri: str):
    global BASE_URI
    BASE_URI = uri


def add_query_params(url: str, **kwargs) -> str:
    set_question_mark = False
    for key, value in kwargs.items():
        if value is not None:
            if not set_question_mark:
                url = f"{url}?{key}={value}"
                set_question_mark = True
            else:
                url = f"{url}&{key}={value}"
    return url


def get_authentication_url() -> str:
    return f"{BASE_URI}/.ory/kratos/public/self-service/login/api"


def get_export_url(project_id: str, **kwargs) -> str:
    url = f"{BASE_URI}/api/project/{project_id}/export"
    url = add_query_params(url, **kwargs)
    return url
