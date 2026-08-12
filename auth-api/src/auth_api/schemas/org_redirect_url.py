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
"""Manager for OrgRedirectUrl schema and export."""

from marshmallow import fields

from auth_api.models.org_redirect_url import OrgRedirectUrl as OrgRedirectUrlModel

from .base_schema import BaseSchema


class OrgRedirectUrlSchema(BaseSchema):  # pylint: disable=too-many-ancestors, too-few-public-methods
    """This is the schema for the OrgRedirectUrl model."""

    class Meta(BaseSchema.Meta):  # pylint: disable=too-few-public-methods
        """Maps all of the OrgRedirectUrl fields to a default schema."""

        model = OrgRedirectUrlModel
        exclude = ("modified_by_id", "modified_by", "modified")

    org_id = fields.Integer(data_key="orgId")
    redirect_url = fields.String(data_key="redirectUrl")
    created = fields.DateTime(data_key="createdDate")
    created_by = fields.Function(
        lambda obj: f"{obj.created_by.firstname} {obj.created_by.lastname}"
        if obj.created_by_id and obj.created_by
        else None,
        data_key="createdBy",
    )
