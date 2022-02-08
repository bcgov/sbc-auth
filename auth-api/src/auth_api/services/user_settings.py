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
"""Service to invoke Rest services."""

from flask import current_app

from auth_api.models.user_settings import UserSettings as UserSettingsModel
from auth_api.services.org import Org as OrgService


class UserSettings:  # pylint: disable=too-few-public-methods
    """Service for user settings."""

    def __init__(self, model):
        """Return an UserSettings Service."""
        self._model = model

    @staticmethod
    def fetch_user_settings(user_id):
        """Create a new organization."""
        current_app.logger.debug('<fetch_user_settings ')

        all_settings = []
        url_origin = current_app.config.get('WEB_APP_URL')
        if user_id:
            all_orgs = OrgService.get_orgs(user_id)
            for org in all_orgs:
                all_settings.append(
                    UserSettingsModel(org.id, org.name, url_origin,
                                      '/account/' + str(org.id) + '/settings',
                                      'ACCOUNT', org.type_code, org.status_code,
                                      '/account/' + str(org.id) + '/restricted-product',
                                      org.branch_name  # added as additonal label
                                      ))

        all_settings.append(UserSettingsModel(user_id, 'USER PROFILE', url_origin, '/userprofile', 'USER_PROFILE'))
        all_settings.append(
            UserSettingsModel(user_id, 'CREATE ACCOUNT', url_origin, '/setup-account', 'CREATE_ACCOUNT'))

        return all_settings
