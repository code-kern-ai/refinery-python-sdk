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


def graphql():
    return f"{get_base_url()}/graphql/"
