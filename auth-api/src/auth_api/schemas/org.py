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
"""Manager for org schema and export."""

from marshmallow import fields, post_dump

from auth_api.models import Org as OrgModel

from .base_schema import BaseSchema


class OrgSchema(BaseSchema):  # pylint: disable=too-many-ancestors, too-few-public-methods
    """This is the schema for the Org model."""

    class Meta(BaseSchema.Meta):  # pylint: disable=too-few-public-methods
        """Maps all of the Org fields to a default schema."""

        model = OrgModel
        exclude = ('members', 'invitations', 'affiliated_entities', 'suspension_reason',
                   'products', 'login_options', 'type_code')

    type_code = fields.String(data_key='org_type')
    status_code = fields.String(data_key='status_code')
    suspension_reason_code = fields.String(data_key='suspension_reason_code')
    business_size = fields.String(data_key='business_size')
    business_type = fields.String(data_key='business_type')
    contacts = fields.Pluck('ContactLinkSchema', 'contact', many=True, data_key='mailing_address')

    @post_dump(pass_many=False)
    def _include_dynamic_fields(self, data, many):
        """Remove all empty values and versions from the dumped dict."""
        if not many:
            if data.get('is_business_account', False):
                # Adding a dynamic field businessName for making other application integrations easy.
                data['businessName'] = data.get('name')
            # Map the mailing address to the first from contact as there can be only one mailing address.

            if (mailing_address := data.get('mailing_address', None)) is not None and mailing_address:
                data['mailing_address'] = mailing_address[0]

        return data
