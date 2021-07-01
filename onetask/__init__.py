# -*- coding: utf-8 -*-

from typing import Callable

from onetask import api_calls
from wasabi import msg

from onetask.labeling_function import unpack_python_function


class Client:

    def __init__(
            self, org_id: str, project_id: str
    ):
        self.org_id = org_id
        self.project_id = project_id

    def get_records(
            self, max_number_samples: int = None
    ):
        raise NotImplementedError

    def register_lf(
            self,
            lf: Callable
    ) -> None:
        fn_name, source_code, description = unpack_python_function(lf)
        _ = api_calls.RegisterLabelingFunctionCall(
            fn_name=fn_name,
            source_code=source_code,
            description=description,
            org_id=self.org_id,
            project_id=self.project_id
        )
        msg.good(f"Registered labeling function '{fn_name}'.")
