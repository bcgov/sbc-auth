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

from auth_api.exceptions import Error, BusinessException
from auth_api.models import Org as OrgModel
from auth_api.services.validators.validator_response import ValidatorResponse
from auth_api.utils.user_context import user_context


@user_context
def validate(validator_response: ValidatorResponse, is_fatal=False, **kwargs) -> None:
    print('--name---------',kwargs)
    name = kwargs.get('name')
    branch_name = kwargs.get('branch_name')
    existing_similar__org = OrgModel.find_similar_org_by_name(name, branch_name=branch_name)
    print('00------existing_similar__org----',existing_similar__org)
    if existing_similar__org is not None:
        validator_response.add_error(Error.DATA_CONFLICT)
        if is_fatal:
            raise BusinessException(Error.DATA_CONFLICT, None)
