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

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base_model import VersionedModel


class ProductSubscriptionRole(VersionedModel):  # pylint: disable=too-few-public-methods
    """Model for a Product Role model."""

    __tablename__ = 'product_subscription_role'

    id = Column(Integer, primary_key=True)
    product_subscription_id = Column(ForeignKey('product_subscription.id'), nullable=False)
    product_role_id = Column(ForeignKey('product_role_code.id'), nullable=False)

    product_role = relationship('ProductRoleCode')
