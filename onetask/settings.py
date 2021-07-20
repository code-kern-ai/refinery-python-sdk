# -*- coding: utf-8 -*-
LOCALHOST_SWITCH = False


def set_to_localhost():
    global LOCALHOST_SWITCH
    LOCALHOST_SWITCH = True


def get_base_url():
    return "http://localhost:8000" if LOCALHOST_SWITCH else "https://app.dev.onetask.ai"


def get_authentication_url():
    return f"{get_base_url()}/.ory/kratos/public/self-service/login/api"


def get_labeling_function_url():
    return f"{get_base_url()}/labelfunction"
