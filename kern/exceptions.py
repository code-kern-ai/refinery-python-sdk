# -*- coding: utf-8 -*-
from typing import Optional

# https://developer.mozilla.org/en-US/docs/Web/HTTP/Status#client_error_responses
class SDKError(Exception):
    def __init__(self, message: Optional[str] = None):
        if message is None:
            message = "Please check the SDK documentation at https://github.com/code-kern-ai/kern-python"
        super().__init__(message)


# 401 Unauthorized
class UnauthorizedError(SDKError):
    pass


# 404 Not Found
class NotFoundError(SDKError):
    pass

class UnknownProjectError(SDKError):
    def __init__(self, project_id: str):
        super().__init__(message=f"Could not find project '{project_id}'. Please check your input.")


# 500 Server Error
class InternalServerError(SDKError):
    pass


class FileImportError(Exception):
    pass

# mirror this from the rest api class ErrorCodes
class ErrorCodes:
    UNRECOGNIZED_USER = "UNRECOGNIZED_USER" # not actively used in SDK
    PROJECT_NOT_FOUND = "PROJECT_NOT_FOUND"


RESPONSE_CODES_API_EXCEPTION_MAP = {
    401: {"*": UnauthorizedError},
    404: {"*": NotFoundError, ErrorCodes.PROJECT_NOT_FOUND: UnknownProjectError},
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
