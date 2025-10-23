"""Application Specific Exceptions, to manage the user errors.

@log_error - a decorator to automatically log the exception to the logger provided

UserException - error, status_code - user rules error
error - a description of the error {code / description: classname / full text}
status_code - where possible use HTTP Error Codes
"""

from auth_api.exceptions.errors import Error  # noqa: I001
from auth_api.exceptions.exception_handler import ExceptionHandler
from auth_api.exceptions.exceptions import (
    BCOLException,
    BusinessException,
    CustomException,
    ServiceUnavailableException,
)
