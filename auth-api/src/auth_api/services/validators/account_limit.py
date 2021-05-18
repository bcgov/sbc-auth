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
"""Util for validating duplication maximum number of orgs."""
from flask import current_app

from auth_api.exceptions import Error, BusinessException
from auth_api.services.validators.validator_response import ValidatorResponse
from auth_api.utils.user_context import user_context, UserContext
from auth_api.models import Org as OrgModel


@user_context
def validate(is_fatal=False, **kwargs) -> ValidatorResponse:
    """Validate account limit for user."""
    user: UserContext = kwargs['user']
    validator_response = ValidatorResponse()
    if not user.is_staff_admin():
        count = OrgModel.get_count_of_org_created_by_user_id(user.user_id)
        if count >= current_app.config.get('MAX_NUMBER_OF_ORGS'):
            validator_response.add_error(Error.MAX_NUMBER_OF_ORGS_LIMIT)
            if is_fatal:
                raise BusinessException(Error.MAX_NUMBER_OF_ORGS_LIMIT, None)
    return validator_response
