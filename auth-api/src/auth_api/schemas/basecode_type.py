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
"""Manager for base type schema and export."""

from marshmallow import fields

from auth_api.models import ma


class BaseCodeSchema(ma.ModelSchema):  # pylint: disable=too-many-ancestors, too-few-public-methods
    """This is the schema for the BaseCode model."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps fields to a default schema."""

        fields = ('code', 'description', 'default', 'is_government_agency', 'is_business')

    # front end expects desc still
    description = fields.String(data_key='desc')
