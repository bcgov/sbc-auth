"""Application Specific Exceptions, to manage the user errors.

@log_error - a decorator to automatically log the exception to the logger provided

UserException - error, status_code - user rules error
error - a description of the error {code / description: classname / full text}
status_code - where possible use HTTP Error Codes
"""
import functools
from auth_api.exceptions.errors import Error


class BusinessException(Exception):
    """Exception that adds error code and error name, that can be used for i18n support."""


    def __init__(self, error: Error, exception: Exception = None, *args, **kwargs):

        """Return a valid BusinessException."""
        super(BusinessException, self).__init__(*args, **kwargs)
        self.message = error.message
        self.code = error.name
        self.status = error.status
        self.detail = exception
        # to do: log/tracing exception
