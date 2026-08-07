# Copyright © 2026 Province of British Columbia
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
"""Entry point for invoking auth-jobs tasks."""

import os
import sys
import time

from cloud_sql_connector import setup_pg8000_close_event_listener, setup_search_path_event_listener
from flask import Flask

import config
from auth_api.utils.logging import setup_logging

setup_logging(os.path.join(os.path.abspath(os.path.dirname(__file__)), "logging.conf"))  # important to do this first


def create_app(run_mode=None):
    """Return a configured Flask App using the Factory method."""
    from auth_api.models import db
    from auth_api.services.gcp_queue import queue

    if run_mode is None:
        run_mode = os.getenv("DEPLOYMENT_ENV", "production")

    app = Flask(__name__)
    app.env = run_mode

    app.config.from_object(config.CONFIGURATION[run_mode])

    app.logger.info("<<<< Starting Auth Jobs >>>>")
    db.init_app(app)
    queue.init_app(app)

    with app.app_context():
        engine = db.engine
        setup_search_path_event_listener(engine, app.config.get("DB_SCHEMA", "public"))
        # Suppress pg8000 InterfaceError on connection close during teardown
        setup_pg8000_close_event_listener(engine)

    register_shellcontext(app)

    return app


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {"app": app}  # pragma: no cover

    app.shell_context_processor(shell_context)


def run(job_name):
    """Run the specified job."""
    from tasks.account_link_notifications import AccountLinkNotificationsTask
    from tasks.adhoc.permission_check import AuthJobPermissionCheckTask

    application = create_app()
    application.app_context().push()

    application.logger.info(f"job_name={job_name} status=started")
    start = time.monotonic()
    try:
        match job_name:
            case "PERMISSION_CHECK":
                AuthJobPermissionCheckTask.check()
            case "ACCOUNT_LINK_NOTIFICATIONS":
                AccountLinkNotificationsTask.notify()
            case _:
                application.logger.warning(f"job_name={job_name} status=unknown_job")
                return

        duration_ms = int((time.monotonic() - start) * 1000)
        application.logger.info(f"job_name={job_name} status=completed duration_ms={duration_ms}")
    except Exception as e:
        duration_ms = int((time.monotonic() - start) * 1000)
        application.logger.error(f"job_name={job_name} status=failed duration_ms={duration_ms} error={e}")
        raise


if __name__ == "__main__":
    print("----------------------------Scheduler Ran With Argument--", sys.argv[1])  # noqa: T201
    run(sys.argv[1])
