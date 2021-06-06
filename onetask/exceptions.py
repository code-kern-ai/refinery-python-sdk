# -*- coding: utf-8 -*-
from typing import Optional


# https://developer.mozilla.org/en-US/docs/Web/HTTP/Status#client_error_responses
class OneTaskError(Exception):
    """
    Base Entity for onetask errors.
    """

    def __init__(self, message: Optional[str] = None):
        if message is None:
            message = "Please check the documentation."
        super().__init__(message)


# 401 Unauthorized
class UnauthorizedError(OneTaskError):
    """
    Entity for errors w.r.t. wrong api token or project id leading to an unauthorized request.
    """


# 422 Unprocessable Entity
class UnprocessableEntityError(OneTaskError):
    """
    Entity for errors w.r.t. custom functions that cannot be executed.
    """


class ParametersError(UnprocessableEntityError):
    """
    Entity for errors w.r.t. custom function signatures that have more than one parameter.
    """


class InvalidOperationError(UnprocessableEntityError):
    """
    Entity for errors w.r.t. custom function operators that are not allowed.
    """


# 404 Not Found
class UnknownIDException(OneTaskError):
    """
    Entity for errors w.r.t. resources that have not been found.
    """


RESPONSE_CODES_EXCEPTION_MAP = {
    401: UnauthorizedError,
    404: UnknownIDException,
    422: {
        "TOO_MANY_PARAMETERS": ParametersError,
        "INVALID_OPERATION": InvalidOperationError,
        "*": UnprocessableEntityError
    }
}


def get_exception_class(
        status_code: int, error_code: Optional[str] = None, error_message: Optional[str] = None
) -> OneTaskError:
    """
    Looks up the correct onetask Error for a given problem.

    :param status_code: HTTP status code returned.
    :param error_code: Specified error code provided by the server.
    :param error_message: Specified error message provided by the server
    :return: Correct onetask Error.
    """
    
    exception_or_dict = RESPONSE_CODES_EXCEPTION_MAP.get(status_code, OneTaskError)
    if isinstance(exception_or_dict, dict):
        exception_class = exception_or_dict.get(error_code, exception_or_dict['*'])
    else:
        exception_class = exception_or_dict
    return exception_class(error_message)
