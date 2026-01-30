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
"""Utility functions for email processors."""

from auth_api.models import Org as OrgModel


def get_account_info(org_id: int | None) -> tuple[str | None, str | None]:
    """Get account name and account name with branch for an org."""
    if not org_id:
        return None, None
    org = OrgModel.find_by_id(org_id)
    account_name = org.name
    account_name_with_branch = org.name
    if org.branch_name:
        account_name_with_branch = f"{org.name} - {org.branch_name}"
    return account_name, account_name_with_branch
