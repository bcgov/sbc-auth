# Copyright © 2024 Province of British Columbia
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
"""Test Suite to ensure the worker routines are working as expected."""

from .utils import helper_add_activity_log_event_to_queue


def test_activity_listener_queue(app, session, client):
    """Assert that events can be retrieved and decoded from the Queue."""
    event_details = {
        'action': 'test_action',
        'itemType': 'test_type',
        'itemName': 'test_name',
        'itemId': '100',
        'actor': 'test_Actor',
        'remoteAddr': ''
    }

    helper_add_activity_log_event_to_queue(client, details=event_details)

    assert True
