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
"""This manages an ProductSubscription Status record in the Auth service.

This is a mapping between status codes and descriptions for ProductSubscription objects.
"""

from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declared_attr

from .base_model import BaseCodeModel


class ProductSubscriptionsStatus(BaseCodeModel):  # pylint: disable=too-few-public-methods
    """This is the model for an ProductSubscription Status record."""

    __tablename__ = "product_subscriptions_statuses"

    @declared_attr
    def code(cls):  # pylint:disable=no-self-argument, # noqa: N805
        """Return column for code."""
        return Column(String(30), primary_key=True)
