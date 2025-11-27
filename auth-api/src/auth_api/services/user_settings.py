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

from auth_api.models import ContactLink as ContactLinkModel
from auth_api.models.user_settings import UserSettings as UserSettingsModel
from auth_api.services.contact import Contact as ContactService
from auth_api.services.org import Org as OrgService


class UserSettings:  # pylint: disable=too-few-public-methods
    """Service for user settings."""

    def __init__(self, model):
        """Return an UserSettings Service."""
        self._model = model

    @staticmethod
    def _fetch_contacts_for_orgs(org_ids):
        """Fetch contacts for multiple orgs in a single batch query.

        Args:
            org_ids: List of organization IDs

        Returns:
            Dictionary mapping org_id to contact dictionary (or None if no contact)
        """
        contacts_by_org = {}
        if not org_ids:
            return contacts_by_org

        contact_links = ContactLinkModel.query.filter(ContactLinkModel.org_id.in_(org_ids)).all()

        for contact_link in contact_links:
            if contact_link.org_id not in contacts_by_org:
                contacts_by_org[contact_link.org_id] = ContactService(contact_link.contact).as_dict()

        return contacts_by_org

    @staticmethod
    def fetch_user_settings(user_id):
        """Create a new organization."""
        current_app.logger.info("<fetch_user_settings ")

        all_settings = []
        url_origin = current_app.config.get("WEB_APP_URL")
        if user_id:
            all_orgs = OrgService.get_orgs(user_id)
            org_ids = [org.id for org in all_orgs]
            contacts_by_org = UserSettings._fetch_contacts_for_orgs(org_ids)
            for org in all_orgs:
                mailing_address_data = contacts_by_org.get(org.id)
                all_settings.append(
                    UserSettingsModel(
                        org.id,
                        org.name,
                        url_origin,
                        "/account/" + str(org.id) + "/settings",
                        "ACCOUNT",
                        org.type_code,
                        org.status_code,
                        "/account/" + str(org.id) + "/restricted-product",
                        org.branch_name,
                        mailing_address_data,
                    )
                )

        all_settings.append(UserSettingsModel(user_id, "USER PROFILE", url_origin, "/userprofile", "USER_PROFILE"))
        all_settings.append(
            UserSettingsModel(user_id, "CREATE ACCOUNT", url_origin, "/setup-account", "CREATE_ACCOUNT")
        )

        return all_settings
