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
"""Manager for contact schema and export."""

from marshmallow import fields, post_dump

from auth_api.models import Contact as ContactModel

from .base_schema import BaseSchema


class ContactSchema(BaseSchema):  # pylint: disable=too-many-ancestors, too-few-public-methods
    """This is the schema for the Contact model."""

    class Meta(BaseSchema.Meta):  # pylint: disable=too-few-public-methods
        """Maps all of the User fields to a default schema."""

        model = ContactModel
        exclude = ('id', 'links', 'created', 'created_by', 'modified', 'modified_by')

    email = fields.String(data_key='email')
    phone = fields.String(data_key='phone')


class ContactSchemaPublic(BaseSchema):
    """This is the public schema for the Contact model it only includes a masked email."""

    class Meta(BaseSchema.Meta):  # pylint: disable=too-few-public-methods
        """Maps all of the User fields to a default schema."""

        model = ContactModel
        exclude = ('id', 'links', 'created', 'created_by', 'modified', 'modified_by', 'phone', 'phone_extension',
                   'postal_code', 'street', 'city', 'region', 'street_additional', 'country', 'delivery_instructions')

    email = fields.String(data_key='email')

    @post_dump(pass_many=False)
    def _mask_email_field(self, data, many):  # pylint: disable=unused-argument
        """Mask email field."""
        email = data.get('email')
        parts = email.split('@')
        if len(parts) == 2:
            username, domain = parts
            masked_username = username[:2] + '*' * (len(username) - 2)
            masked_domain = domain[:2] + '*' * (len(domain) - 2)
            data['email'] = masked_username + '@' + masked_domain
        return data
