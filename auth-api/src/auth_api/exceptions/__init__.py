"""Application Specific Exceptions, to manage the user errors.

@log_error - a decorator to automatically log the exception to the logger provided

UserException - error, status_code - user rules error
error - a description of the error {code / description: classname / full text}
status_code - where possible use HTTP Error Codes
"""
from http import HTTPStatus

import traceback

from sbc_common_components.tracing.exception_tracing import ExceptionTracing  # noqa: I001, I003

from auth_api.exceptions.errors import Error  # noqa: I001, I003


class BusinessException(Exception):  # noqa: N818
    """Exception that adds error code and error name, that can be used for i18n support."""

    def __init__(self, error, exception, *args, **kwargs):
        """Return a valid BusinessException."""
        super().__init__(*args, **kwargs)

        self.message = error.message
        self.error = error.message
        self.code = error.name
        self.status_code = error.status_code
        self.detail = exception

        # log/tracing exception
        ExceptionTracing.trace(self, traceback.format_exc())


class ServiceUnavailableException(Exception):  # noqa: N818
    """Exception to be raised if third party service is unavailable."""

    def __init__(self, error, *args, **kwargs):
        """Return a valid ServiceUnavailableException."""
        super().__init__(*args, **kwargs)
        self.error = error
        self.status_code = Error.SERVICE_UNAVAILABLE.name


class CustomException:
    """A custom exception object to be used propagate errors."""

    def __init__(self, message, status_code, name=None):
        """Return a Custom exception when enum cant be used."""
        self.message = message
        self.status_code = status_code
        self.name = name
