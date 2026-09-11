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

"""Tests to assure the Permission Check.

Test-Suite to ensure that the AuthJobPermissionCheckTask can be invoked.
"""

from unittest.mock import patch

from tasks.adhoc.permission_check import AuthJobPermissionCheckTask


def test_permission_check(session, app):
    """Test permission check publishes to both the account mailer and activity log topics."""
    with patch("tasks.adhoc.permission_check.queue.publish") as mock_publish:
        AuthJobPermissionCheckTask.check()

    published_topics = [call.args[0] for call in mock_publish.call_args_list]
    assert published_topics == [app.config.get("ACCOUNT_MAILER_TOPIC"), app.config.get("AUTH_EVENT_TOPIC")]
