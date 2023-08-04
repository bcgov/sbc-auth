# Copyright © 2023 Province of British Columbia
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
"""Manager for affiliation invitation schema and export."""

from marshmallow import fields

from auth_api.models import AffiliationInvitation as AffiliationInvitationModel

from .base_schema import BaseSchema


class AffiliationInvitationSchema(BaseSchema):  # pylint: disable=too-many-ancestors, too-few-public-methods
    """This is the schema for the invitation model."""

    class Meta(BaseSchema.Meta):  # pylint: disable=too-few-public-methods
        """Maps all of the invitation fields to a default schema."""

        model = AffiliationInvitationModel
        fields = (
            'id', 'from_org', 'to_org', 'business_identifier', 'recipient_email', 'sent_date', 'expires_on',
            'accepted_date', 'status', 'token', 'type', 'affiliation_id')

    from_org = fields.Nested('OrgSchema', only=('id', 'name', 'org_type'))
    to_org = fields.Nested('OrgSchema', only=('id', 'name', 'org_type'))
    business_identifier = fields.String(attribute='entity.business_identifier', data_key='businessIdentifier')
