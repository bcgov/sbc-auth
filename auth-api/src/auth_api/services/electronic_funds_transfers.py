# Copyright © 2023 Province of British Columbia
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
"""Service for managing Affiliation data."""
import datetime
import re
from typing import Dict, List

from flask import current_app
from requests.exceptions import HTTPError
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001
from sqlalchemy.orm import contains_eager, subqueryload

from auth_api.exceptions import BusinessException, ServiceUnavailableException
from auth_api.exceptions.errors import Error
from auth_api.models import db
from auth_api.models.affiliation import Affiliation as AffiliationModel
from auth_api.models.affiliation_invitation import AffiliationInvitation as AffiliationInvitationModel
from auth_api.models.contact_link import ContactLink
from auth_api.models.dataclass import Activity
from auth_api.models.dataclass import Affiliation as AffiliationData
from auth_api.models.dataclass import DeleteAffiliationRequest
from auth_api.models.entity import Entity
from auth_api.models.membership import Membership as MembershipModel
from auth_api.schemas import AffiliationSchema
from auth_api.services.entity import Entity as EntityService
from auth_api.services.org import Org as OrgService
from auth_api.services.user import User as UserService
from auth_api.utils.enums import ActivityAction, CorpType, NRActionCodes, NRNameStatus, NRStatus
from auth_api.utils.passcode import validate_passcode
from auth_api.utils.roles import ALL_ALLOWED_ROLES, CLIENT_AUTH_ROLES, STAFF
from auth_api.utils.user_context import UserContext, user_context
from .activity_log_publisher import ActivityLogPublisher
from .rest_service import RestService


@ServiceTracing.trace(ServiceTracing.enable_tracing, ServiceTracing.should_be_tracing)
class ElectronicFundsTransfersService:
    """Manages Electronic Funds Transfers Service short name data."""

    @staticmethod
    def get_electronic_funds_transfers_short_names(include_all: bool, page: int, limit: int):
        """Get the NR payment details."""
        include_all = True
        pay_api_url = current_app.config.get('PAY_API_URL')
        electronic_funds_transfers = RestService.get(
            f'{pay_api_url}/eft-shortnames?includeAll={include_all}?page={page}&limit={limit}',
            token=RestService.get_service_account_token()
        ).json()
        return electronic_funds_transfers
