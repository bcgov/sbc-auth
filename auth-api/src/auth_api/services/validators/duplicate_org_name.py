# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Util for validating duplication in account name."""

from auth_api.exceptions import BusinessException, Error
from auth_api.models import Org as OrgModel
from auth_api.services.validators.validator_response import ValidatorResponse
from auth_api.utils.user_context import user_context


@user_context
def validate(is_fatal=False, **kwargs) -> ValidatorResponse:
    """Validate and return org name."""
    name = kwargs.get('name')
    branch_name = kwargs.get('branch_name')
    org_id = kwargs.get('org_id', None)
    validator_response = ValidatorResponse()
    existing_similar_orgs = OrgModel.find_similar_org_by_name(name, org_id=org_id, branch_name=branch_name)
    if existing_similar_orgs:
        validator_response.add_error(Error.DATA_CONFLICT)
        if is_fatal:
            raise BusinessException(Error.DATA_CONFLICT, None)
    return validator_response
