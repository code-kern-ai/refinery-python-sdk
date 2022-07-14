# -*- coding: utf-8 -*-
BASE_URI: str
DEFAULT_URI: str = "https://app.kern.ai"


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


def get_project_url(project_id: str) -> str:
    return f"{BASE_URI}/api/project/{project_id}"


def get_lookup_list_url(project_id: str, lookup_list_id: str) -> str:
    return f"{get_project_url(project_id)}/lookup_list/{lookup_list_id}"


def get_records_url(project_id: str) -> str:
    return f"{get_project_url(project_id)}/records"


def get_export_url(project_id: str) -> str:
    return f"{get_project_url(project_id)}/export"


def get_import_url(project_id: str) -> str:
    return f"{get_project_url(project_id)}/import"


def get_base_config(project_id: str) -> str:
    return f"{get_project_url(project_id)}/import/base_config"


def get_task(project_id: str, task_id: str) -> str:
    return f"{get_project_url(project_id)}/import/task/{task_id}"
