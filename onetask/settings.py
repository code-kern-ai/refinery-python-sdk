# -*- coding: utf-8 -*-
STAGE: str


def set_stage(stage):
    global STAGE
    STAGE = stage


def get_base_url():
    global STAGE
    if STAGE == "prod":
        return "https://app.onetask.ai"
    elif STAGE == "test":
        return "https://app.test.onetask.ai"
    elif STAGE == "dev":
        return "https://app.dev.onetask.ai"
    else:
        return "http://localhost:8000"


def get_authentication_url():
    return f"{get_base_url()}/.ory/kratos/public/self-service/login/api"


def get_labeling_function_url():
    return f"{get_base_url()}/labelfunction"
