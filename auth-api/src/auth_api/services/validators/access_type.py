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
"""Util for validating access type against each user roles."""

from auth_api.exceptions import Error
from auth_api.services.validators.validator_response import ValidatorResponse
from auth_api.utils.enums import AccessType
from auth_api.utils.user_context import UserContext, user_context


@user_context
def validate(**kwargs) -> ValidatorResponse:
    """Validate and return correct access type."""
    access_type: str = kwargs.get('accessType')
    user: UserContext = kwargs['user_context']
    error = None
    validator_response = ValidatorResponse()
    if access_type:
        if not user.is_staff_admin() and access_type in AccessType.ANONYMOUS.value:
            error = Error.USER_CANT_CREATE_ANONYMOUS_ORG
        if not user.is_staff_admin() and access_type in AccessType.GOVM.value:
            error = Error.USER_CANT_CREATE_GOVM_ORG
        if not user.is_bceid_user() and access_type in \
                (AccessType.EXTRA_PROVINCIAL.value, AccessType.REGULAR_BCEID.value):
            error = Error.USER_CANT_CREATE_EXTRA_PROVINCIAL_ORG
        if user.is_bceid_user() and access_type not in \
                (AccessType.EXTRA_PROVINCIAL.value, AccessType.REGULAR_BCEID.value, AccessType.GOVN.value):
            error = Error.USER_CANT_CREATE_REGULAR_ORG
        if error is not None:
            validator_response.add_error(error)
            return validator_response
    else:
        # If access type is not provided, add default value based on user
        if user.is_bceid_user():
            access_type = AccessType.EXTRA_PROVINCIAL.value
        elif not user.is_staff_admin():
            access_type = AccessType.REGULAR.value
    validator_response.add_info({'access_type': access_type})
    return validator_response
