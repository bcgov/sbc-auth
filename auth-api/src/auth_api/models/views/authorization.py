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

from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import expression

from auth_api.models.db import db
from auth_api.utils.roles import ADMIN, COORDINATOR, USER


class Authorization(db.Model):
    """This is the model the authorizations_view."""

    __tablename__ = 'authorizations_view'

    business_identifier = Column(String)
    entity_name = Column(String)
    org_membership = Column(String)
    keycloak_guid = Column(UUID)
    org_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, primary_key=True)
    org_type = Column(String)
    corp_type_code = Column(String)
    product_code = Column(String)
    org_name = Column(String)
    bcol_user_id = Column(String)
    bcol_account_id = Column(String)
    folio_number = Column(String)
    status_code = Column(String)

    @classmethod
    def find_user_authorization_by_business_number(cls, business_identifier: str, keycloak_guid: uuid = None,
                                                   org_id: int = None, is_staff=None):
        """Return authorization view object."""
        auth = None
        if keycloak_guid and business_identifier and org_id:
            auth = cls.query.filter_by(keycloak_guid=keycloak_guid,
                                       business_identifier=business_identifier,
                                       org_id=org_id).one_or_none()
        elif business_identifier and org_id:
            auth = cls.query.filter_by(business_identifier=business_identifier,
                                       org_id=org_id).first()
        elif keycloak_guid and business_identifier:
            auth = cls.query.filter_by(keycloak_guid=keycloak_guid,
                                       business_identifier=business_identifier).first()
        elif is_staff and business_identifier:
            auth = cls.query.filter_by(business_identifier=business_identifier).first()
        return auth

    @classmethod
    def find_user_authorization_by_business_number_and_product(cls, business_identifier: str, product_code: str):
        """Return authorization view object using corp type and business identifier.

        Mainly used for service accounts.Sorted using the membership since service accounts gets all access

        """
        return cls.query.filter_by(product_code=product_code, business_identifier=business_identifier) \
            .order_by(expression.case(((Authorization.org_membership == ADMIN, 1),
                                       (Authorization.org_membership == COORDINATOR, 2),
                                       (Authorization.org_membership == USER, 3)))) \
            .first()

    @classmethod
    def find_user_authorization_by_org_id(cls, keycloak_guid: uuid, org_id: int):
        """Return authorization view object."""
        return cls.query.filter_by(keycloak_guid=keycloak_guid, org_id=org_id).one_or_none()

    @classmethod
    def find_authorization_for_admin_by_org_id(cls, org_id: int):
        """Return authorization view object for staff."""
        # staff gets ADMIN level access
        return cls.query.filter_by(org_id=org_id, org_membership=ADMIN).first()

    @classmethod
    def find_account_authorization_by_org_id_and_product_for_user(cls, keycloak_guid: uuid, org_id: int, product: str):
        """Return authorization view object."""
        return cls.query.filter_by(keycloak_guid=keycloak_guid, org_id=org_id, product_code=product).one_or_none()

    @classmethod
    def find_account_authorization_by_org_id_and_product(cls, org_id: int, product: str):
        """Return authorization view object."""
        return cls.query.filter_by(org_id=org_id, product_code=product, org_membership=ADMIN).first()

    @classmethod
    def find_all_authorizations_for_user(cls, keycloak_guid):
        """Return list of authorizations for the user."""
        return cls.query.filter_by(keycloak_guid=keycloak_guid).all()
