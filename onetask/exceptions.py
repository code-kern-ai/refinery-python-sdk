# -*- coding: utf-8 -*-
from typing import Optional


class ClientError(Exception):
    def __init__(self, message: Optional[str] = None):
        if message is None:
            message = "Please check the documentation."
        super().__init__(message)


class ParameterError(ClientError):
    pass


# https://developer.mozilla.org/en-US/docs/Web/HTTP/Status#client_error_responses
class APIError(Exception):
    def __init__(self, message: Optional[str] = None):
        if message is None:
            message = "Please check the API reference."
        super().__init__(message)


# 401 Unauthorized
class UnauthorizedError(APIError):
    pass


# 404 Not Found
class UnknownIDException(APIError):
    pass


RESPONSE_CODES_API_EXCEPTION_MAP = {
    401: UnauthorizedError,
    404: UnknownIDException,
}


def get_api_exception_class(
        status_code: int, error_code: Optional[str] = None, error_message: Optional[str] = None
) -> APIError:
    exception_or_dict = RESPONSE_CODES_API_EXCEPTION_MAP.get(status_code, APIError)
    if isinstance(exception_or_dict, dict):
        exception_class = exception_or_dict.get(error_code, exception_or_dict['*'])
    else:
        exception_class = exception_or_dict
    return exception_class(error_message)
