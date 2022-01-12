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
"""Service to check status of service(s)."""
import json

import arrow
from flask import current_app


LOCAL_TIMEZONE = 'US/Pacific'


class Status:
    """Service to check status of service(s)."""

    def __init__(self):
        """Return a User Service object."""

    @classmethod
    def check_status(cls, service_name: str, check_date: arrow.Arrow):
        """Check service scheduled status. The check date should be UTC datetime format."""
        current_status = 'None'
        up_time = 0

        response = {
            'service': service_name,
            'current_status': current_status,
            'next_up_time': up_time
        }

        if not service_name or not check_date:
            return response

        check_date_local = check_date.to(LOCAL_TIMEZONE)
        service_schedule = cls.get_schedules(service_name)
        if service_schedule:
            current_app.logger.debug(f'check date: {check_date_local}')

            current_status = 'True'
            outage_times = cls.get_outage_schedules(service_schedule)
            available_times = cls.get_available_schedules(service_schedule, check_date_local)

            for outage in outage_times:
                if check_date_local.date() >= outage[0].date() and (outage[0] < check_date_local < outage[1]):
                    current_app.logger.debug(f'outage date: start {outage[0]} end {outage[1]}')
                    current_status = 'False'
                    up_time = outage[1].timestamp

            if current_status == 'True':
                if 'available' in service_schedule[0]:

                    for available in available_times:
                        if check_date_local.date() == available[0].date() \
                                and (check_date_local < available[0] or check_date_local > available[1]):
                            current_app.logger.debug(f'available date: from {available[0]} to {available[1]}')

                            current_status = 'False'
                            up_time = available[0].timestamp

            # Add any custom message is provided
            custom = service_schedule[0].get('custom', None)
            if custom is not None:
                if (Status._get_local_outage_time(custom['start'])
                        <= check_date_local
                        < Status._get_local_outage_time(custom['end'])):
                    response['custom_message'] = custom['message']

            response['current_status'] = current_status
            if up_time:
                response['next_up_time'] = up_time
                response['message'] = current_app.config.get('PAYBC_OUTAGE_MESSAGE')

        return response

    @staticmethod
    def get_schedules(service_name: str):
        """Get schedules from configuration by service name."""
        schedule_json: list = json.loads(current_app.config.get('SERVICE_SCHEDULE'))
        service_schedule = list(filter(lambda x: x.get('service_name') == service_name, schedule_json))

        return service_schedule

    @staticmethod
    def get_available_schedules(service_schedule: list, check_date_local: arrow.Arrow):
        """Get available schedules from schedules."""
        week_dates: list = []
        date_availables: list = []

        check_date_only: arrow.Arrow = check_date_local.replace(hour=0, minute=0, second=0, microsecond=0)
        for day_week in range(-1, 7):
            week_dates.append(check_date_only.shift(days=day_week))

        if 'available' in service_schedule[0]:
            for available_time in service_schedule[0]['available']:
                for day_week in week_dates:
                    if day_week.isoweekday() == int(available_time['dayofweek']):
                        from_hours, from_minutes = map(int, available_time['from'].split(':'))
                        to_hours, to_minutes = map(int, available_time['to'].split(':'))
                        date_availables.append([day_week.replace(hour=from_hours, minute=from_minutes),
                                                day_week.replace(hour=to_hours, minute=to_minutes)])

        return date_availables

    @staticmethod
    def get_outage_schedules(service_schedule: list):
        """Get outage schedules from schedules."""
        date_outages: list = []

        if 'outage' in service_schedule[0]:
            for outage_time in service_schedule[0]['outage']:
                start_date = Status._get_local_outage_time(outage_time['start'])
                end_date = Status._get_local_outage_time(outage_time['end'])
                date_outages.append([start_date, end_date])

        return date_outages

    @staticmethod
    def _get_local_outage_time(outage_time: str):
        return arrow.get(outage_time, 'YYYY-MM-DD HH:mm').replace(tzinfo=LOCAL_TIMEZONE)
