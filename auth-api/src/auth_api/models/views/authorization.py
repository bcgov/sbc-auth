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
"""This manages Authorization view.

Authorization view wraps details on the entities and membership through orgs and delegations.
"""

import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from auth_api.models.db import db


class Authorization(db.Model):
    """This is the model the authorizations_view."""

    __tablename__ = 'authorizations_view'

    business_identifier = Column(String, primary_key=True)
    entity_name = Column(String)
    role = Column(String)
    keycloak_guid = Column(UUID)

    @classmethod
    def find_user_authorization_by_business_number(cls, keycloak_guid: uuid, business_identifier: str):
        """Return authorization view object."""
        return cls.query.filter_by(keycloak_guid=keycloak_guid, business_identifier=business_identifier).one_or_none()

    @classmethod
    def find_all_authorizations_for_user(cls, keycloak_guid):
        """Return list of authorizations for the user."""
        return cls.query.filter_by(keycloak_guid=keycloak_guid).all()
