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
"""Exposes all of the resource endpoints mounted in Flask-Blueprint style.

Uses restplus namespaces to mount individual api endpoints into the service.

All services have 2 defaults sets of endpoints:
 - ops
 - meta
That are used to expose operational health information about the service, and meta information.
"""

from flask import Blueprint, current_app
# noqa: I001, I003, I004
from sbc_common_components.exception_handling.exception_handler import ExceptionHandler

from .account import API as ACCOUNTS_API
from .acitivity_log import API as ACTIVITY_LOG_API
from .affiliation_invitation import API as AFFILIATION_INVITATION_API
from .apihelper import Api
from .bcol_profiles import API as BCOL_PROFILE_API
from .bulk_user import API as BULK_USER_API
from .codes import API as CODES_API
from .documents import API as DOCUMENTS_API
from .documents_affidavit import API as DOCUMENTS_AFFIDAVIT_API
from .entity import API as ENTITY_API
from .invitation import API as INVITATION_API
from .meta import API as META_API
from .notifications import API as NOTIFICATIONS_API
from .ops import API as OPS_API
from .org import API as ORG_API
from .org_api_keys import API as ORG_API_KEYS_API
from .org_authorizations import API as ORG_AUTHORISATION_API
from .org_products import API as ORG_PRODUCTS_API
from .permissions import API as PERMISSIONS_API
from .products import API as PRODUCTS_API
from .reset import API as RESET_API
from .task import API as TASKS_API
from .user import API as USER_API
from .user_settings import API as USER_SETTINGS_API


__all__ = ('API_BLUEPRINT', 'OPS_BLUEPRINT')

# This will add the Authorize button to the swagger docs
# TODO oauth2 & openid may not yet be supported by restplus <- check on this
AUTHORIZATIONS = {'apikey': {'type': 'apiKey', 'in': 'header', 'name': 'Authorization'}}

OPS_BLUEPRINT = Blueprint('API_OPS', __name__, url_prefix='/ops')

API_OPS = Api(
    OPS_BLUEPRINT,
    title='Service OPS API',
    version='1.0',
    description='The Core API for the Authentication System',
    security=['apikey'],
    authorizations=AUTHORIZATIONS,
)

API_OPS.add_namespace(OPS_API, path='/')

API_BLUEPRINT = Blueprint('API', __name__, url_prefix='/api/v1')

API = Api(
    API_BLUEPRINT,
    title='Authentication API',
    version='1.0',
    description='The Core API for the Authentication System',
    security=['apikey'],
    authorizations=AUTHORIZATIONS,
)

HANDLER = ExceptionHandler(API)

API.add_namespace(META_API, path='/meta')
API.add_namespace(USER_API, path='/users')
API.add_namespace(BULK_USER_API, path='/bulk/users')
API.add_namespace(USER_SETTINGS_API, path='/users/<string:user_id>/settings')
API.add_namespace(ENTITY_API, path='/entities')
API.add_namespace(ORG_API, path='/orgs')
API.add_namespace(AFFILIATION_INVITATION_API, path='/affiliationInvitations')
API.add_namespace(INVITATION_API, path='/invitations')
API.add_namespace(DOCUMENTS_API, path='/documents')
API.add_namespace(DOCUMENTS_AFFIDAVIT_API, path='/documents/affidavit')
API.add_namespace(CODES_API, path='/codes')
API.add_namespace(ACCOUNTS_API, path='/accounts')
API.add_namespace(ORG_PRODUCTS_API, path='/orgs/<int:org_id>/products')
API.add_namespace(PRODUCTS_API, path='/products')
API.add_namespace(NOTIFICATIONS_API, path='/users/<string:user_id>/org/<int:org_id>/notifications')
API.add_namespace(USER_API, path='/users/<string:invitation_token>')
API.add_namespace(BCOL_PROFILE_API, path='/bcol-profiles')
API.add_namespace(PERMISSIONS_API, path='/permissions')
API.add_namespace(ORG_AUTHORISATION_API, path='/orgs/<int:org_id>/authorizations')
API.add_namespace(ORG_API_KEYS_API, path='/orgs/<int:org_id>/api-keys')
API.add_namespace(TASKS_API, path='/tasks')
API.add_namespace(ACTIVITY_LOG_API, path='/orgs/<int:org_id>/activity-logs')

TEST_BLUEPRINT = Blueprint('TEST', __name__, url_prefix='/test')

API_TEST = Api(
    TEST_BLUEPRINT,
    title='Authentication API for testing',
    version='1.0',
    description='The API for the testing',
    security=['apikey'],
    authorizations=AUTHORIZATIONS,
)

HANDLER = ExceptionHandler(API_TEST)

API_TEST.add_namespace(RESET_API, path='/reset')
