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
"""Super class to handle all operations related to base schema."""

from marshmallow import fields, post_dump

from auth_api.models import ma


class BaseSchema(ma.ModelSchema):  # pylint: disable=too-many-ancestors
    """Base Schema."""

    def __init__(self, *args, **kwargs):
        """Excludes versions. Otherwise database will query <name>_versions table."""
        if hasattr(self.opts.model, 'versions') and (len(self.opts.fields) == 0):
            self.opts.exclude += ('versions',)
        super().__init__(*args, **kwargs)

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta class to declare any class attributes."""

        datetimeformat = '%Y-%m-%dT%H:%M:%S+00:00'  # Default output date format.

    created_by = fields.Function(
        lambda obj: f'{obj.created_by.firstname} {obj.created_by.lastname}' if obj.created_by else None
    )

    modified_by = fields.Function(
        lambda obj: f'{obj.modified_by.firstname} {obj.modified_by.lastname}' if obj.modified_by else None
    )

    @post_dump(pass_many=True)
    def _remove_empty(self, data, many):
        """Remove all empty values and versions from the dumped dict."""
        if not many:
            for key in list(data):
                if key == 'versions':
                    data.pop(key)

            return {
                key: value for key, value in data.items()
                if value is not None
            }
        for item in data:
            for key in list(item):
                if (key == 'versions') or (item[key] is None):
                    item.pop(key)

        return data
