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
"""This model manages a subscribed products by an account (org).

The ProductSubscription object connects Org models to one or more ProductSubscription models.
"""

from sqlalchemy import Column, ForeignKey, Integer, and_
from sqlalchemy.orm import relationship

from ..utils.roles import VALID_SUBSCRIPTION_STATUSES
from .base_model import VersionedModel


class ProductSubscription(VersionedModel):  # pylint: disable=too-few-public-methods
    """Model for a Product Subscription model."""

    __tablename__ = 'product_subscriptions'

    id = Column(Integer, primary_key=True)
    org_id = Column(ForeignKey('orgs.id'), nullable=False, index=True)
    product_code = Column(ForeignKey('product_codes.code'), nullable=False)

    product = relationship('ProductCode', foreign_keys=[product_code], lazy='select')
    status_code = Column(ForeignKey('product_subscriptions_statuses.code'), nullable=False)
    product_subscriptions_status = relationship('ProductSubscriptionsStatus')

    @classmethod
    def find_by_org_id(cls, org_id, valid_statuses=VALID_SUBSCRIPTION_STATUSES):
        """Find an product subscription instance that matches the provided id."""
        return cls.query.filter(
            and_(ProductSubscription.org_id == org_id, ProductSubscription.status_code.in_(valid_statuses))).all()

    @classmethod
    def find_by_org_id_product_code(cls, org_id, product_code, valid_statuses=VALID_SUBSCRIPTION_STATUSES):
        """Find an product subscription instance that matches the provided id."""
        return cls.query.filter(
            and_(ProductSubscription.org_id == org_id, ProductSubscription.product_code == product_code,
                 ProductSubscription.status_code.in_(valid_statuses))).all()
