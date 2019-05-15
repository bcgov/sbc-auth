"""Application Specific Exceptions, to manage the user errors.

@log_error - a decorator to automatically log the exception to the logger provided

UserException - error, status_code - user rules error
error - a description of the error {code / description: classname / full text}
status_code - where possible use HTTP Error Codes
"""
import functools


class UserException(Exception):
    """Exception that adds error code and error name, that can be used for i18n support."""

    def __init__(self, error, status_code, trace_back, *args, **kwargs):
        """Return a valid UserException."""
        super(UserException, self).__init__(*args, **kwargs)
        self.error = error
        self.status_code = status_code
        self.trace_back = trace_back
