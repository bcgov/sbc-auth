# Copyright © 2025 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Centralized setup of logging for the service."""

import logging
import logging.config
import sys
from os import path

from structured_logging import StructuredLogging


def setup_logging(conf):
    """Create the services logger."""
    if conf and path.isfile(conf):
        logging.config.fileConfig(conf)
        print(f"Configure logging, from conf:{conf}", file=sys.stdout)  # noqa: T201
    else:
        print(f"Unable to configure logging, attempted conf:{conf}", file=sys.stderr)  # noqa: T201


class StructuredLogHandler(logging.Handler):
    """StructuredLogHandler that wraps StructuredLogging."""

    def __init__(self, structured_logger=None):
        """Initialize the StructuredLogHandler."""
        super().__init__()
        self.structured_logger = structured_logger or StructuredLogging.get_logger()

    def emit(self, record):
        """Emit a record."""
        msg = self.format(record)
        level = record.levelname.lower()

        if level == "debug":
            self.structured_logger.debug(msg)
        elif level == "info":
            self.structured_logger.info(msg)
        elif level == "warning":
            self.structured_logger.warning(msg)
        elif level == "error":
            self.structured_logger.error(msg)
        elif level == "critical":
            self.structured_logger.critical(msg)
