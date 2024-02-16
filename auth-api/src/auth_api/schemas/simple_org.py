# Copyright © 2024 Province of British Columbia
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
"""Manager for simple org schema and export."""

from attrs import define

from auth_api.models import Org


@define
class SimpleOrgInfoSchema:  # pylint: disable=too-few-public-methods
    """Main schema used to serialize simplified org information."""

    id: int
    name: str
    branch_name: str
    status: str

    @classmethod
    def from_row(cls, row: Org):
        """From row is used so we don't tightly couple to our database class.

        https://www.attrs.org/en/stable/init.html
        """
        return cls(id=row.id,
                   name=row.name,
                   branch_name=row.branch_name,
                   status=row.status_code)
