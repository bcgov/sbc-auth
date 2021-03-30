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
"""Manager for staff tasks schema and export."""

from auth_api.models import StaffTask as StaffTaskModel

from .base_schema import BaseSchema


class StaffTaskSchema(BaseSchema):
    """This is the schema for the StaffTask model."""

    class Meta:
        """Maps all of the StaffTask fields to a default schema."""

        model = StaffTaskModel
