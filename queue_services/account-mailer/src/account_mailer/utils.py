# Copyright © 2019 Province of British Columbia
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
"""Supply version and commit hash info.

When deployed in OKD, it adds the last commit hash onto the version info.
"""
import os
from datetime import datetime

import pytz
from flask import current_app

from account_mailer.version import __version__


def _get_build_openshift_commit_hash():
    return os.getenv('OPENSHIFT_BUILD_COMMIT', None)


def get_run_version():
    """Return a formatted version string for this service."""
    commit_hash = _get_build_openshift_commit_hash()
    if commit_hash:
        return f'{__version__}-{commit_hash}'
    return __version__


def get_local_time(date_val: datetime):
    """Return local time value."""
    tz_name = current_app.config['LEGISLATIVE_TIMEZONE']
    tz_local = pytz.timezone(tz_name)
    date_val = date_val.astimezone(tz_local)
    return date_val


def get_local_formatted_date(date_val: datetime, dt_format: str = '%Y-%m-%d'):
    """Return formatted local time."""
    return get_local_time(date_val).strftime(dt_format)
