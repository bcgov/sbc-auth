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
"""This manages an Org Status record in the Auth service.

This is a mapping between status codes and descriptions for Org objects.
"""

from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declared_attr

from .base_model import BaseCodeModel


class OrgStatus(BaseCodeModel):  # pylint: disable=too-few-public-methods # Temporarily disable until methods defined
    """This is the model for an Org Status record."""

    __tablename__ = "org_statuses"

    @declared_attr
    def code(cls):  # pylint:disable=no-self-argument, # noqa: N805
        """Return column for code."""
        return Column(String(30), primary_key=True)

    @classmethod
    def get_default_status(cls):
        """Return the default status code for an Org."""
        return cls.query.filter_by(default=True).first()
