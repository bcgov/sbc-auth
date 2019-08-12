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
"""This manages an Org Type record in the Auth service.

This is a mapping between org type codes and descriptions for Org objects.
"""

from sqlalchemy import Column, String

from .db import db


class OrgType(db.Model):  # pylint: disable=too-few-public-methods # Temporarily disable until methods defined
    """This is the model for an Org Type record."""

    __tablename__ = 'org_type'

    code = Column(String(15), primary_key=True, unique=True)
    desc = Column(String(100))
