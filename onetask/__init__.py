# -*- coding: utf-8 -*-

from typing import Callable, List

from onetask import api_calls, settings
from wasabi import msg

from onetask.labeling_function import build_keywords_lf, unpack_python_function


class Client:
    def __init__(
        self, user_name: str, password: str, project_id: str, debug: bool = False
    ):
        if not debug:
            self.session_token = api_calls.create_session_token(
                user_name=user_name, password=password
            )
            if self.session_token is not None:
                msg.good("Logged in to system.")
            else:
                msg.fail("Could not log in. Please check your username and password.")
        else:
            self.session_token = None
            settings.set_to_localhost()
            msg.info("Sending requests to localhost")
        self.project_id = project_id

    def register_custom_lf(self, lf: Callable) -> None:
        fn_name, source_code, description = unpack_python_function(lf)
        _ = api_calls.RegisterLabelingFunctionCall(
            fn_name=fn_name,
            source_code=source_code,
            description=description,
            project_id=self.project_id,
            session_token=self.session_token,
        )
        msg.good(f"Registered labeling function '{fn_name}'.")

    def register_keywords_lf(
        self,
        label: str,
        keywords: List[str],
        attributes: List[str],
        lowercase: bool = True,
    ):
        fn_name, source_code, description = build_keywords_lf(
            label, keywords, attributes, lowercase
        )
        _ = api_calls.RegisterLabelingFunctionCall(
            fn_name=fn_name,
            source_code=source_code,
            description=description,
            project_id=self.project_id,
            session_token=self.session_token,
        )
        msg.good(f"Registered labeling function '{fn_name}'.")
