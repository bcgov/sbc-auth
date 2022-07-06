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
"""Auth Utils.

Generic utils to help auth functions.
"""

from auth_api.models import User as UserModel
from auth_api.utils.enums import Status
from flask import current_app


def get_member_emails(org_id, roles):
    """Get emails for the user role passed in."""
    member_list = UserModel.find_users_by_org_id_by_status_by_roles(org_id, roles, Status.ACTIVE.value)
    member_emails = ','.join([str(x.contacts[0].contact.email) for x in member_list if x.contacts])
    return member_emails


def get_login_url():
    """Get application login url."""
    login_url = current_app.config.get('WEB_APP_URL')
    return login_url
