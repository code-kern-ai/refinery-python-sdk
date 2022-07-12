# -*- coding: utf-8 -*-
from typing import Optional

# https://developer.mozilla.org/en-US/docs/Web/HTTP/Status#client_error_responses
class SDKError(Exception):
    def __init__(self, message: Optional[str] = None):
        if message is None:
            message = (
                "Please check the SDK documentation at https://docs.kern.ai/reference."
            )
        super().__init__(message)


# 401 Unauthorized
class UnauthorizedError(SDKError):
    pass


# 404 Not Found
class NotFoundError(SDKError):
    pass


# 500 Server Error
class InternalServerError(SDKError):
    pass


class FileImportError(Exception):
    pass


RESPONSE_CODES_API_EXCEPTION_MAP = {
    401: {"*": UnauthorizedError},
    404: {"*": NotFoundError},
    500: {"*": InternalServerError},
}


def get_api_exception_class(
    status_code: int,
    error_code: Optional[str] = None,
    error_message: Optional[str] = None,
) -> SDKError:
    exception_or_dict = RESPONSE_CODES_API_EXCEPTION_MAP.get(status_code, SDKError)
    if isinstance(exception_or_dict, dict):
        exception_class = exception_or_dict.get(error_code, exception_or_dict["*"])
    else:
        exception_class = exception_or_dict
    return exception_class(error_message)
