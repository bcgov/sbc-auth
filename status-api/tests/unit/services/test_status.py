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

"""Tests to assure the Status check service layer.

Test-Suite to ensure that the Status Service layer is working as expected.
"""
from datetime import datetime, timedelta
from unittest.mock import patch

import arrow

from status_api.services.status import Status as StatusService


def test_check_status(app):
    """Assert that the function returns schedules."""
    with app.app_context():
        service_name = 'PAYBC'

        response = StatusService.check_status(service_name=service_name, check_date=arrow.Arrow.utcnow())
        assert response is not None
        assert response['service'] == service_name

        response = StatusService.check_status(service_name=None, check_date=arrow.Arrow.utcnow())
        assert response is not None
        assert response['service'] is None
        assert response['current_status'] == 'None'
        assert response['next_up_time'] == 0

        response = StatusService.check_status(service_name=service_name, check_date=None)
        assert response is not None
        assert response['service'] == service_name
        assert response['current_status'] == 'None'
        assert response['next_up_time'] == 0

        service_name = 'PAYBC1'
        response = StatusService.check_status(service_name=service_name, check_date=arrow.Arrow.utcnow())
        assert response is not None
        assert response['service'] == service_name
        assert response['current_status'] == 'None'
        assert response['next_up_time'] == 0


def test_check_status_without_schedule(app):
    """Assert that the function return correct response without schedule setup."""
    with app.app_context():
        service_name = 'PAYBC'

        # without service schedule setup
        schedule_json = None
        mock_get_schedule = patch('status_api.services.status.Status.get_schedules')
        mock_get = mock_get_schedule.start()
        mock_get.return_value = schedule_json
        response = StatusService().check_status(service_name=service_name, check_date=arrow.Arrow.utcnow())
        mock_get.stop()

        assert response is not None
        assert response['service'] == service_name
        assert response['current_status'] == 'None'
        assert response['next_up_time'] == 0

        # without service outage and available schedule setup expect return no outage
        schedule_json = [{'service_name': 'PAYBC'}]
        mock_get_schedule = patch('status_api.services.status.Status.get_schedules')
        mock_get = mock_get_schedule.start()
        mock_get.return_value = schedule_json
        response = StatusService().check_status(service_name=service_name, check_date=arrow.Arrow.utcnow())
        mock_get.stop()

        assert response is not None
        assert response['service'] == service_name
        assert response['current_status'] == 'True'
        assert response['next_up_time'] == 0


def test_get_outage_schedule(app):
    """Assert that the get outage schedule function return correct response."""
    schedule_json = [
        {
            'available': [
                {'dayofweek': '1', 'from': '6:00', 'to': '21:00'},
                {'dayofweek': '2', 'from': '6:00', 'to': '21:00'},
                {'dayofweek': '3', 'from': '6:00', 'to': '21:00'},
                {'dayofweek': '4', 'from': '15:05', 'to': '21:00'},
                {'dayofweek': '5', 'from': '6:00', 'to': '21:00'},
                {'dayofweek': '6', 'from': '6:30', 'to': '21:00'},
                {'dayofweek': '7', 'from': '6:30', 'to': '21:00'}
            ],
            'outage': [
                {'start': '2019-10-23 16:00', 'end': '2019-10-23 18:00'},
                {'start': '2019-10-23 16:00', 'end': '2019-10-23 17:00'},
                {'start': '2019-10-23 13:00', 'end': '2019-10-25 15:05'}
            ]
        }
    ]

    with app.app_context():
        response = StatusService().get_outage_schedules(schedule_json)

        assert response is not None
        assert response[0][0] == arrow.get('2019-10-23 16:00', 'YYYY-MM-DD HH:mm').replace(tzinfo='US/Pacific')
        assert response[2][1] == arrow.get('2019-10-25 15:05', 'YYYY-MM-DD HH:mm').replace(tzinfo='US/Pacific')

        schedule_json = [
            {
                'available': [
                    {'dayofweek': '1', 'from': '6:00', 'to': '21:00'},
                    {'dayofweek': '2', 'from': '6:00', 'to': '21:00'},
                    {'dayofweek': '3', 'from': '6:00', 'to': '21:00'},
                    {'dayofweek': '4', 'from': '15:05', 'to': '21:00'},
                    {'dayofweek': '5', 'from': '6:00', 'to': '21:00'},
                    {'dayofweek': '6', 'from': '6:30', 'to': '21:00'},
                    {'dayofweek': '7', 'from': '6:30', 'to': '21:00'}
                ]
            }
        ]

        response = StatusService().get_outage_schedules(schedule_json)

        assert response is not None
        assert len(response) == 0


def test_get_available_schedule(app):
    """Assert that the get availabe schedule function return correct response."""
    schedule_json = [
        {
            'available': [
                {'dayofweek': '1', 'from': '6:00', 'to': '21:00'},
                {'dayofweek': '2', 'from': '6:00', 'to': '21:00'},
                {'dayofweek': '3', 'from': '6:00', 'to': '21:00'},
                {'dayofweek': '4', 'from': '15:05', 'to': '21:00'},
                {'dayofweek': '5', 'from': '6:00', 'to': '21:00'},
                {'dayofweek': '6', 'from': '6:30', 'to': '21:00'},
                {'dayofweek': '7', 'from': '6:30', 'to': '21:00'}
            ],
            'outage': [
                {'start': '2019-10-23 16:00', 'end': '2019-10-23 18:00'},
                {'start': '2019-10-23 16:00', 'end': '2019-10-23 17:00'},
                {'start': '2019-10-23 13:00', 'end': '2019-10-25 15:05'}
            ]
        }
    ]

    check_date: arrow.Arrow = arrow.get('2019-10-23 10:00', 'YYYY-MM-DD HH:mm')
    check_date_local: arrow.Arrow = check_date.replace(tzinfo='US/Pacific')

    with app.app_context():
        response = StatusService().get_available_schedules(schedule_json, check_date_local)

        assert response is not None
        assert response[0][0] == arrow.get('2019-10-28 06:00:00', 'YYYY-MM-DD HH:mm:ss').replace(tzinfo='US/Pacific')

        schedule_json = [
            {
                'outage': [
                    {'start': '2019-10-23 16:00', 'end': '2019-10-23 18:00'},
                    {'start': '2019-10-23 16:00', 'end': '2019-10-23 17:00'},
                    {'start': '2019-10-23 13:00', 'end': '2019-10-25 15:05'}
                ]
            }
        ]

        response = StatusService().get_available_schedules(schedule_json, check_date_local)

        assert response is not None
        assert len(response) == 0


def test_check_status_no_outage(app):
    """Assert that the function returns schedules."""
    schedule_json = [
        {
            'available': [
                {'dayofweek': '1', 'from': '6:00', 'to': '21:00'},
                {'dayofweek': '2', 'from': '6:00', 'to': '21:00'},
                {'dayofweek': '3', 'from': '6:00', 'to': '21:00'},
                {'dayofweek': '4', 'from': '15:05', 'to': '21:00'},
                {'dayofweek': '5', 'from': '6:00', 'to': '21:00'},
                {'dayofweek': '6', 'from': '6:30', 'to': '21:00'},
                {'dayofweek': '7', 'from': '6:30', 'to': '21:00'}
            ],
            'outage': [
                {'start': '2019-10-23 10:00', 'end': '2019-10-23 18:00'},
                {'start': '2019-10-24 13:00', 'end': '2019-10-25 15:05'}
            ]
        }
    ]

    with app.app_context():
        service_name = 'PAYBC'
        #  Localtime: Sunday, November 24, 2019 10:00:00 AM GMT-08:00
        check_date: arrow.Arrow = arrow.get('2019-11-24 18:00', 'YYYY-MM-DD HH:mm')

        mock_get_schedule = patch('status_api.services.status.Status.get_schedules')
        mock_get = mock_get_schedule.start()
        mock_get.return_value = schedule_json
        response = StatusService().check_status(service_name=service_name, check_date=check_date)
        mock_get.stop()

        # no outage, match available schedule
        assert response is not None
        assert response['service'] == service_name
        assert response['current_status'] == 'True'


def test_check_status_with_outage(app):
    """Assert that the function returns schedules."""
    schedule_json = [
        {
            'available': [
                {'dayofweek': '1', 'from': '6:00', 'to': '21:00'},
                {'dayofweek': '2', 'from': '6:00', 'to': '21:00'},
                {'dayofweek': '3', 'from': '6:00', 'to': '21:00'},
                {'dayofweek': '4', 'from': '15:05', 'to': '21:00'},
                {'dayofweek': '5', 'from': '6:00', 'to': '21:00'},
                {'dayofweek': '6', 'from': '6:30', 'to': '21:00'},
                {'dayofweek': '7', 'from': '6:30', 'to': '21:00'}
            ],
            'outage': [
                {'start': '2019-10-23 10:00', 'end': '2019-10-23 18:00'},
                {'start': '2019-10-24 13:00', 'end': '2019-10-25 15:05'}
            ]
        }
    ]

    with app.app_context():
        service_name = 'PAYBC'
        #  Localtime: Wednesday, October 23, 2019 3:00:00 PM GMT-07:00
        check_date: arrow.Arrow = arrow.get('2019-10-23 22:00', 'YYYY-MM-DD HH:mm')

        mock_get_schedule = patch('status_api.services.status.Status.get_schedules')
        mock_get = mock_get_schedule.start()
        mock_get.return_value = schedule_json
        response = StatusService().check_status(service_name=service_name, check_date=check_date)
        mock_get.stop()

        # match outage windows
        assert response is not None
        assert response['service'] == service_name
        assert response['current_status'] == 'False'

        #  Localtime:  Friday, October 25, 2019 5:00:00 AM GMT-07:00
        check_date: arrow.Arrow = arrow.get('2019-10-25 12:00', 'YYYY-MM-DD HH:mm')

        mock_get_schedule = patch('status_api.services.status.Status.get_schedules')
        mock_get = mock_get_schedule.start()
        mock_get.return_value = schedule_json
        response = StatusService().check_status(service_name=service_name, check_date=check_date)
        mock_get.stop()

        # match outage windows
        assert response is not None
        assert response['service'] == service_name
        assert response['current_status'] == 'False'
        assert response['message'] == 'Test'


def test_check_status_with_custom(app):
    """Assert that the function returns schedules."""
    time_yday = datetime.now() - timedelta(days=1)
    time_tomorrow = time_yday + timedelta(days=2)

    time_str = arrow.get(time_yday).replace(tzinfo='US/Pacific').strftime('%Y-%m-%d %H:%M')
    time_tomorrow_str = arrow.get(time_tomorrow).replace(tzinfo='US/Pacific').strftime('%Y-%m-%d %H:%M')

    schedule_json = [
        {
            'custom': {
                'start': time_str, 'end': time_tomorrow_str, 'message': 'Test-Warning'
            }

        }
    ]

    with app.app_context():
        service_name = 'PAYBC'
        # Test the custom message for today
        check_date: arrow.Arrow = arrow.get(datetime.now())

        mock_get_schedule = patch('status_api.services.status.Status.get_schedules')
        mock_get = mock_get_schedule.start()
        mock_get.return_value = schedule_json
        response = StatusService().check_status(service_name=service_name, check_date=check_date)
        mock_get.stop()

        # match outage windows
        assert response is not None
        assert response['service'] == service_name
        assert response['custom_message'] == 'Test-Warning'

        # Test the custom message for 1 day and 1 sec from now and custom_message should not be present
        time_day_after = time_tomorrow + timedelta(days=1)
        check_date: arrow.Arrow = arrow.get(time_day_after)

        mock_get_schedule = patch('status_api.services.status.Status.get_schedules')
        mock_get = mock_get_schedule.start()
        mock_get.return_value = schedule_json
        response = StatusService().check_status(service_name=service_name, check_date=check_date)
        mock_get.stop()

        # match outage windows
        assert response is not None
        assert response['service'] == service_name
        assert response.get('custom_message', None) is None
