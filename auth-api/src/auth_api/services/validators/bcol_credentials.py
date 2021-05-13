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
import json

from flask import current_app

from auth_api import status as http_status
from auth_api.exceptions import Error, BusinessException, CustomException
from auth_api.services.rest_service import RestService
from auth_api.services.validators.validator_response import ValidatorResponse
from auth_api.utils.user_context import user_context, UserContext


@user_context
def validate(validator_response: ValidatorResponse, is_fatal=False, **kwargs) -> None:
    bcol_credential = kwargs.get('bcol_credential')
    org_id = kwargs.get('org_id', None)
    user: UserContext = kwargs['user']
    bcol_response = RestService.post(endpoint=current_app.config.get('BCOL_API_URL') + '/profiles',
                                     data=bcol_credential, token=user.bearer_token, raise_for_status=False)

    if bcol_response.status_code != http_status.HTTP_200_OK:
        error = json.loads(bcol_response.text)
        validator_response.add_error(
            CustomException(error['detail'], bcol_response.status_code))
        if is_fatal:
            raise BusinessException(CustomException(error['detail'], bcol_response.status_code), None)
        bcol_account_number = bcol_response.json().get('accountNumber')
        from auth_api.services.org import Org as OrgService
        if OrgService.bcol_account_link_check(bcol_account_number, org_id):
            validator_response.add_error(
                Error.BCOL_ACCOUNT_ALREADY_LINKED)
            if is_fatal:
                raise BusinessException(Error.BCOL_ACCOUNT_ALREADY_LINKED, None)
        return
    print('----------bcol_responsebcol_response-------------',bcol_response.json())
    validator_response.add_response({'bcol_response': bcol_response})
