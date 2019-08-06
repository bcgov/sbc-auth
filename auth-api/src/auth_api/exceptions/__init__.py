"""Application Specific Exceptions, to manage the user errors.

@log_error - a decorator to automatically log the exception to the logger provided

UserException - error, status_code - user rules error
error - a description of the error {code / description: classname / full text}
status_code - where possible use HTTP Error Codes
"""

import traceback
from functools import wraps

from sbc_common_components.tracing.exception_tracing import ExceptionTracing

from auth_api.exceptions.errors import Error


class BusinessException(Exception):
    """Exception that adds error code and error name, that can be used for i18n support."""

    def __init__(self, error, exception, *args, **kwargs):
        """Return a valid BusinessException."""
        super(BusinessException, self).__init__(*args, **kwargs)

        self.message = error.message
        self.error = error.message
        self.code = error.name
        self.status_code = error.status_code
        self.detail = exception

        # log/tracing exception
        ExceptionTracing.trace(self, traceback.format_exc())


class UserException(Exception):
    """Exception that adds error code and error name, that can be used for i18n support."""

    def __init__(self, error, status_code, trace_back, *args, **kwargs):
        """Return a valid UserException."""
        super(UserException, self).__init__(*args, **kwargs)
        self.error = error
        self.status_code = status_code
        self.trace_back = trace_back


def catch_custom_exception(func):
    """TODO just a demo function."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BusinessException as e:
            trace_back = traceback.format_exc()
            ExceptionTracing.trace(e, trace_back)
            raise UserException(e.with_traceback(None), e.status_code, trace_back)

    return decorated_function


def catch_business_exception(func):
    """Catch and raise exception."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise BusinessException(Error.UNDEFINED_ERROR, e)

    return decorated_function
