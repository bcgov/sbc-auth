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

from sqlalchemy import Column, String, Integer, and_, or_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import expression

from auth_api.models.db import db
from auth_api.utils.roles import ADMIN, MEMBER, OWNER


class Authorization(db.Model):
    """This is the model the authorizations_view."""

    __tablename__ = 'authorizations_view'

    business_identifier = Column(String)
    entity_name = Column(String)
    org_membership = Column(String)
    keycloak_guid = Column(UUID, primary_key=True)
    org_id = Column(Integer, primary_key=True)
    org_type = Column(String)
    corp_type_code = Column(String)

    @classmethod
    def find_user_authorization_by_business_number(cls, keycloak_guid: uuid, business_identifier: str):
        """Return authorization view object."""
        return cls.query.filter_by(keycloak_guid=keycloak_guid, business_identifier=business_identifier).one_or_none()

    @classmethod
    def find_user_authorization_by_business_number_and_corp_type(cls, business_identifier: str, corp_type: str):
        """Return authorization view object using corp type and business identifier.

        Mainly used for service accounts.Sorted using the membership since service accounts gets all access

        """
        return cls.query.filter_by(corp_type_code=corp_type, business_identifier=business_identifier) \
            .order_by(expression.case(((Authorization.org_membership == OWNER, 1),
                                       (Authorization.org_membership == ADMIN, 2),
                                       (Authorization.org_membership == MEMBER, 3)))) \
            .first()

    @classmethod
    def find_user_authorization_by_org_id(cls, keycloak_guid: uuid, org_id: int):
        """Return authorization view object."""
        return cls.query.filter_by(keycloak_guid=keycloak_guid, org_id=org_id).one_or_none()

    @classmethod
    def find_user_authorization_by_org_id_and_corp_type(cls, org_id: int, corp_type: str):
        """Return authorization view object."""
        return db.session.query(Authorization).filter(
            and_(Authorization.org_id == org_id,
                 or_(Authorization.corp_type_code == corp_type, Authorization.corp_type_code.is_(None)))).order_by(
            expression.case(((Authorization.org_membership == OWNER, 1),
                             (Authorization.org_membership == ADMIN, 2),
                             (Authorization.org_membership == MEMBER, 3)))).first()

    @classmethod
    def find_all_authorizations_for_user(cls, keycloak_guid):
        """Return list of authorizations for the user."""
        return cls.query.filter_by(keycloak_guid=keycloak_guid).all()
