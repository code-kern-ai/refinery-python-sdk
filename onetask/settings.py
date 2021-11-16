# -*- coding: utf-8 -*-
STAGE: str


def set_stage(stage):
    global STAGE
    STAGE = stage


def get_base_url():
    global STAGE
    if STAGE == "beta":
        return "https://app.beta.onetask.ai"
    elif STAGE == "test":
        return "https://app.test.onetask.ai"
    elif STAGE == "dev":
        return "https://app.dev.onetask.ai"
    elif STAGE == "local":
        return "http://localhost:4455"
    else:
        return STAGE


def get_authentication_url():
    return f"{get_base_url()}/.ory/kratos/public/self-service/login/api"


def get_project_url(project_id):
    return f"{get_base_url()}/api/project/{project_id}"


def get_post_lf_url():
    return f"{get_base_url()}/labelfunction"


def get_schema_url(project_id):
    return f"{get_project_url(project_id)}/schema"


def get_embeddings_url(project_id, config_string):
    return f"{get_project_url(project_id)}/embeddings/{config_string}"


def get_data_url(project_id, manually_labeled):
    url = f"{get_project_url(project_id)}/data"
    if manually_labeled:
        url = f"{url}?labelled=manual"
    return url
