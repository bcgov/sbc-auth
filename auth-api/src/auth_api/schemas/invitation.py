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
"""Manager for invitation schema and export."""

from marshmallow import fields

from auth_api.models import Invitation as InvitationModel

from .base_schema import BaseSchema
from .invitation_membership import InvitationMembershipSchema


class InvitationSchema(BaseSchema):  # pylint: disable=too-many-ancestors, too-few-public-methods
    """This is the schema for the invitation model."""

    class Meta(BaseSchema.Meta):  # pylint: disable=too-few-public-methods
        """Maps all of the invitation fields to a default schema."""

        model = InvitationModel
        fields = (
            "id",
            "recipient_email",
            "sent_date",
            "expires_on",
            "accepted_date",
            "status",
            "membership",
            "token",
            "type",
        )

    membership = fields.Nested(InvitationMembershipSchema, many=True)
