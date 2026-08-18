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
"""Manager for AuthorizedAccount schema and export."""

from marshmallow import Schema, fields


class AuthorizedAccountSchema(Schema):  # pylint: disable=too-few-public-methods
    """Schema for an account on the View Access screen.

    A flat projection over an affiliation and its org rather than a dump of a single model. 
    dateAdded comes from the affiliation (when the account was given access),
    not from the org (when it was opened).
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta class to declare any class attributes."""

        datetimeformat = "%Y-%m-%dT%H:%M:%S+00:00"

    name = fields.String(attribute="org.name")
    branch_name = fields.String(attribute="org.branch_name", data_key="branchName")
    # bool() so that a NULL column serializes as false and the UI never has to null check.
    is_business_account = fields.Function(
        lambda affiliation: bool(affiliation.org.is_business_account), data_key="isBusinessAccount"
    )
    uuid = fields.String(attribute="org.uuid")
    date_added = fields.DateTime(attribute="created", data_key="dateAdded")
