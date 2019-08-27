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
"""Manager for entity schema and export."""

from marshmallow import fields

from auth_api.models import Entity as EntityModel

from .base_schema import BaseSchema


class EntitySchema(BaseSchema):  # pylint: disable=too-many-ancestors, too-few-public-methods
    """Used to manage the default mapping between JSON and the Entity model."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps all of the Entity fields to a default schema."""

        model = EntityModel
        exclude = ('id', 'pass_code')

    business_identifier = fields.String(data_key='businessIdentifier')
    business_number = fields.String(data_key='businessNumber')
    pass_code_claimed = fields.Boolean(data_key='passCodeClaimed')
    contacts = fields.Pluck('ContactLinkSchema', 'contact', many=True)
