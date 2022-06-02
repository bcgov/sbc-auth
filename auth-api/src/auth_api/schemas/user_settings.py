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
"""Manager for User settings schema and export."""

from marshmallow import post_dump

from auth_api.models import ma


class UserSettingsSchema(ma.ModelSchema):  # pylint: disable=too-many-ancestors, too-few-public-methods
    """This is the schema for the User Settings model."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps all of the User Settings fields to a default schema."""

        fields = ('id', 'label', 'additional_label', 'urlorigin', 'urlpath', 'type', 'account_type', 'account_status',
                  'product_settings')

    @post_dump(pass_many=True)
    def _remove_empty(self, data, many):
        """Remove all empty values from the dumped dict."""
        if not many:
            return {
                key: value for key, value in data.items()
                if value or isinstance(value, float)
            }
        for item in data:
            for key in list(item):
                value = item[key]
                if not value and not isinstance(value, float):
                    item.pop(key)
        return data
