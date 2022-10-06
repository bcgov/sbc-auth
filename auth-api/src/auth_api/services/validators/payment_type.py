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
from flask import current_app

from auth_api.exceptions import BusinessException, Error
from auth_api.services.validators.validator_response import ValidatorResponse
from auth_api.utils.enums import AccessType, OrgType, PaymentMethod
from auth_api.utils.user_context import user_context


@user_context
def validate(is_fatal=False, **kwargs) -> ValidatorResponse:
    """Validate and return correct access type."""
    selected_payment_method: str = kwargs.get('selected_payment_method')
    access_type: str = kwargs.get('access_type')
    org_type: str = kwargs.get('org_type')
    default_cc_method = PaymentMethod.DIRECT_PAY.value if current_app.config.get(
        'DIRECT_PAY_ENABLED') else PaymentMethod.CREDIT_CARD.value
    validator_response = ValidatorResponse()
    non_ejv_payment_methods = (
            PaymentMethod.CREDIT_CARD.value, PaymentMethod.DIRECT_PAY.value,
            PaymentMethod.PAD.value, PaymentMethod.BCOL.value)
    org_payment_method_mapping = {
        OrgType.BASIC: (
            PaymentMethod.CREDIT_CARD.value, PaymentMethod.DIRECT_PAY.value, PaymentMethod.ONLINE_BANKING.value),
        OrgType.PREMIUM: non_ejv_payment_methods,
        OrgType.SBC_STAFF: non_ejv_payment_methods,
        OrgType.STAFF: non_ejv_payment_methods,
    }
    if access_type == AccessType.GOVM.value:
        payment_type = PaymentMethod.EJV.value
    elif selected_payment_method:
        valid_types = org_payment_method_mapping.get(org_type, [])
        if selected_payment_method in valid_types:
            payment_type = selected_payment_method
        else:
            validator_response.add_error(
                Error.INVALID_INPUT)
            if is_fatal:
                raise BusinessException(Error.INVALID_INPUT, None)
    else:
        premium_org_types = (OrgType.PREMIUM, OrgType.SBC_STAFF, OrgType.STAFF)
        payment_type = PaymentMethod.BCOL.value if \
            org_type in premium_org_types else default_cc_method
    validator_response.add_info({'payment_type': payment_type})
    return validator_response
