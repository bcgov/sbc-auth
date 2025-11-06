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
"""Date utility functions."""

import datetime as dt

import pytz


def str_to_utc_dt(date: str, add_time: bool):
    """Convert ISO formatted dates into dateTime objects in UTC."""
    time_zone = pytz.timezone("Canada/Pacific")
    naive_dt = dt.datetime.strptime(date, "%Y-%m-%d")
    local_dt = time_zone.localize(naive_dt, is_dst=None)
    if add_time:
        local_dt = dt.datetime(local_dt.year, local_dt.month, local_dt.day, 23, 59, 59)
    utc_dt = local_dt.astimezone(pytz.utc)

    return utc_dt
