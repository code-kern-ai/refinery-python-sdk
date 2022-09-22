# -*- coding: utf-8 -*-
from typing import Optional


class LocalError(Exception):
    pass


class UnknownItemError(LocalError):
    pass


class PrimaryKeyError(LocalError):
    pass


# https://developer.mozilla.org/en-US/docs/Web/HTTP/Status#client_error_responses
class APIError(Exception):
    def __init__(self, project_id: str, message: Optional[str] = None):
        self.project_id = project_id
        if message is None:
            message = "Please check the SDK documentation at https://github.com/code-kern-ai/refinery-python"
        super().__init__(message)


# 401 Unauthorized
class UnauthorizedError(APIError):
    def __init__(self, project_id: str, message: Optional[str] = None):
        super().__init__(project_id, message)


# 403 Forbidden
class ForbiddenError(APIError):
    def __init__(
        self,
        project_id: str,
        message="You can't access the project with your current role.",
    ):
        super().__init__(project_id, message)


# 404 Not Found
class NotFoundError(APIError):
    pass


class UnknownProjectError(APIError):
    def __init__(self, project_id: str, message: Optional[str] = None):
        super().__init__(
            project_id,
            f"Could not find project '{project_id}'. Please check your input.",
        )


# 500 Server Error
class InternalServerError(APIError):
    def __init__(self, project_id: str, message: Optional[str] = None):
        super().__init__(project_id, message)


class FileImportError(Exception):
    pass


# mirror this from the rest api class ErrorCodes
class ErrorCodes:
    UNRECOGNIZED_USER = "UNRECOGNIZED_USER"  # not actively used in SDK
    FORBIDDEN_USER = "FORBIDDEN_USER"
    PROJECT_NOT_FOUND = "PROJECT_NOT_FOUND"


RESPONSE_CODES_API_EXCEPTION_MAP = {
    401: {"*": UnauthorizedError},
    403: {"*": ForbiddenError},
    404: {"*": NotFoundError, ErrorCodes.PROJECT_NOT_FOUND: UnknownProjectError},
    500: {"*": InternalServerError},
}


def get_api_exception_class(
    status_code: int,
    error_code: Optional[str] = None,
    error_message: Optional[str] = None,
    project_id: Optional[str] = None,
) -> APIError:
    exception_or_dict = RESPONSE_CODES_API_EXCEPTION_MAP.get(status_code, APIError)
    if isinstance(exception_or_dict, dict):
        exception_class = exception_or_dict.get(error_code, exception_or_dict["*"])
        return exception_class(project_id=project_id)
    else:
        return exception_or_dict(project_id=project_id, message=error_message)
