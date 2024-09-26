# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Function to handle all exceptions."""
import traceback

from flask import request
from flask_jwt_oidc import AuthError
from sqlalchemy.exc import SQLAlchemyError
from structured_logging import StructuredLogging
from werkzeug.exceptions import HTTPException, default_exceptions

logger = StructuredLogging.get_logger()

RESPONSE_HEADERS = {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}


class ExceptionHandler:
    """Class to handle exceptions."""

    def __init__(self, app=None):
        """Private constructor."""
        if app:
            self.init_app(app)

    def auth_handler(self, error):  # pylint: disable=useless-option-value
        """Handle AuthError."""
        logger.error(error.error)
        return error.error, error.status_code, RESPONSE_HEADERS

    def db_handler(self, error):  # pylint: disable=useless-option-value
        """Handle Database error."""
        stack_trace = traceback.format_exc()
        message_text = str(error.__dict__["orig"]) if "orig" in error.__dict__ else "Internal server error"
        error_message = f"{{error: {message_text}, stack_trace: {stack_trace}}}"
        logger.exception(error_message)
        error_text = error.__dict__["code"] if hasattr(error.__dict__, "code") else ""
        status_code = error.status_code if hasattr(error, "status_code") else 500
        return {"error": "{}".format(error_text), "message": "{}".format(message_text)}, status_code, RESPONSE_HEADERS

    def std_handler(self, error):  # pylint: disable=useless-option-value
        """Handle standard exception."""
        if isinstance(error, HTTPException):
            logger.error(f"{{error code: {error.code}, path: {request.path}}}")
            message = dict(message=error.description, path=request.path)
        else:
            stack_trace = traceback.format_exc()
            error_message = f"{{error: {error}, stack_trace: {stack_trace}}}"
            logger.exception(error_message)
            message = dict(message="Internal server error")

        return message, error.code if isinstance(error, HTTPException) else 500, RESPONSE_HEADERS

    def init_app(self, app):
        """Register common exceptons or errors."""
        self.app = app
        self.register(AuthError, self.auth_handler)
        self.register(SQLAlchemyError, self.db_handler)
        self.register(Exception)
        for exception in default_exceptions:
            self.register(self._get_exc_class_and_code(exception))

    def register(self, exception_or_code, handler=None):
        """Register exception with handler."""
        self.app.errorhandler(exception_or_code)(handler or self.std_handler)

    @staticmethod
    def _get_exc_class_and_code(exc_class_or_code):
        """Get the exception class being handled.

        For HTTP status codes or ``HTTPException`` subclasses, return both the exception and status code.

        :param exc_class_or_code: Any exception class, or an HTTP status code as an integer.
        """
        if isinstance(exc_class_or_code, int):
            exc_class = default_exceptions[exc_class_or_code]
        else:
            exc_class = exc_class_or_code

        assert issubclass(exc_class, Exception)

        return exc_class
