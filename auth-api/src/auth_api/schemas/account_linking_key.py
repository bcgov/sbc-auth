# Copyright © 2026 Province of British Columbia
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
"""Manager for AccountLinkingKey schema and export."""

from marshmallow import fields

from auth_api.models import AccountLinkingKey as AccountLinkingKeyModel

from .base_schema import BaseSchema


class AccountLinkingKeySchema(BaseSchema):  # pylint: disable=too-many-ancestors, too-few-public-methods
    """This is the schema for the AccountLinkingKey model."""

    class Meta(BaseSchema.Meta):  # pylint: disable=too-few-public-methods
        """Maps all of the AccountLinkingKey fields to a default schema."""

        model = AccountLinkingKeyModel
        exclude = ("created_by_id", "modified_by_id", "modified_by", "modified")

    linking_key = fields.String(data_key="linkingKey")
    account_id = fields.Integer(data_key="accountId")
    vendor_account_id = fields.Integer(data_key="vendorAccountId", allow_none=True)
    vendor_account_name = fields.Method("get_vendor_account_name", data_key="vendorAccountName")
    expires_on = fields.DateTime(data_key="expiresOn")
    last_used = fields.DateTime(data_key="lastUsed", allow_none=True)
    created = fields.DateTime(data_key="createdOn")
    created_by = fields.Function(
        lambda obj: f"{obj.created_by.firstname} {obj.created_by.lastname}"
        if obj.created_by_id and obj.created_by
        else None,
        data_key="createdBy",
    )

    def get_vendor_account_name(self, obj):
        """Return the vendor org name."""
        return obj.vendor_account.name if obj.vendor_account else None
