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
"""Manager for affiliation schema and export."""

from marshmallow import fields

from auth_api.models import Affiliation as AffiliationModel

from .base_schema import BaseSchema


class AffiliationSchema(BaseSchema):  # pylint: disable=too-many-ancestors, too-few-public-methods
    """This is the schema for the Affiliation model."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps all of the Affiliation fields to a default schema."""

        model = AffiliationModel

    entity = fields.Nested('EntitySchema', many=False)
    org = fields.Nested('OrgSchema', many=False)
