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
"""The ActivityLog service.

This module manages the activity logs.
"""

from flask import current_app
from jinja2 import Environment, FileSystemLoader
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api.models import ActivityLog as ActivityLogModel
from auth_api.schemas import ActivityLogSchema
from auth_api.services.authorization import check_auth
from auth_api.utils.enums import ActivityAction
from auth_api.utils.roles import ADMIN, STAFF, Role
from auth_api.utils.user_context import UserContext, user_context

ENV = Environment(loader=FileSystemLoader('.'), autoescape=True)


@ServiceTracing.trace(ServiceTracing.enable_tracing, ServiceTracing.should_be_tracing)
class ActivityLog:  # pylint: disable=too-many-instance-attributes
    """Manages all aspects of the Activity Log Entity."""

    def __init__(self, model):
        """Return a activity log service."""
        self._model: ActivityLogModel = model

    @property
    def identifier(self):
        """Return the identifier for this user."""
        return self._model.id

    @ServiceTracing.disable_tracing
    def as_dict(self):
        """Return the Activity Log as a python dict.

        None fields are not included in the dict.
        """
        activity_log_schema = ActivityLogSchema()
        obj = activity_log_schema.dump(self._model, many=False)
        return obj

    @staticmethod
    @user_context
    def fetch_activity_logs(org_id: int, **kwargs):  # pylint: disable=too-many-locals
        """Search all activity logs."""
        user_from_context: UserContext = kwargs['user_context']
        item_name = kwargs.get('item_name')
        item_type = kwargs.get('item_type')
        action = kwargs.get('action')
        check_auth(one_of_roles=(ADMIN, STAFF), org_id=org_id)
        logs = {'activity_logs': []}
        page: int = int(kwargs.get('page'))
        limit: int = int(kwargs.get('limit'))
        search_args = (item_name,
                       item_type,
                       action,
                       page,
                       limit)

        current_app.logger.debug('<fetch_activity logs ')
        results, count = ActivityLogModel.fetch_activity_logs_for_account(org_id, *search_args)
        is_staff_access = user_from_context.is_staff()
        for result in results:
            activity_log: ActivityLogModel = result[0]
            log_dict = ActivityLogSchema(exclude=('actor_id',)).dump(activity_log)

            if user := result[1]:
                actor = ActivityLog._mask_user_name(is_staff_access, user)
                log_dict['actor'] = actor
            log_dict['action'] = ActivityLog._build_string(activity_log, actor)
            logs['activity_logs'].append(log_dict)

        logs['total'] = count
        logs['page'] = page
        logs['limit'] = limit

        current_app.logger.debug('>fetch_activity logs')
        return logs

    @staticmethod
    def _build_string(activity: ActivityLogModel, actor) -> str:
        action = activity.get('action')
        return {
            ActivityAction.INVITE_TEAM_MEMBER.value: ActivityLog._inviting_team_member(activity, actor),
            ActivityAction.APPROVE_TEAM_MEMBER.value: ActivityLog._approving_new_team_member(activity, actor),
            ActivityAction.REMOVE_TEAM_MEMBER.value: ActivityLog._removing_team_member(activity, actor),
            ActivityAction.RESET_2FA.value: ActivityLog._twofactor_reset(activity, actor),
            ActivityAction.PAYMENT_INFO_CHANGE.value: ActivityLog._payment_info_change(activity, actor),
            ActivityAction.CREATE_AFFILIATION.value: ActivityLog._adding_a_business_affilliation(activity, actor),
            ActivityAction.REMOVE_AFFILIATION.value: ActivityLog._removing_a_business_affilliation(activity, actor),
            ActivityAction.ACCOUNT_NAME_CHANGE.value: ActivityLog._account_name_changes(activity, actor),
            ActivityAction.AUTHENTICATION_METHOD_CHANGE.value:
            ActivityLog._authentication_method_changes(activity, actor),
            ActivityAction.ACCOUNT_SUSPENSION.value: ActivityLog._account_suspension(activity),
            ActivityAction.ADD_PRODUCT_AND_SERVICE.value: ActivityLog._adding_products_and_services(activity, actor),
            ActivityAction.REMOVE_PRODUCT_AND_SERVICE.value:
            ActivityLog._removing_products_and_services(activity, actor)
        }.get(action, action)

    @staticmethod
    def _inviting_team_member(activity: ActivityLogModel, actor: str) -> str:
        """User X invited User Y as a [role name]."""
        return f'{actor} invited {activity.item_name} as a {activity.item_value}'

    @staticmethod
    def _approving_new_team_member(activity: ActivityLogModel, actor: str) -> str:
        """User X approved User Y joining the team as [role name]."""
        return f'{actor} approved {activity.item_name} \
            joining the team as {activity.item_value}'

    @staticmethod
    def _removing_team_member(activity: ActivityLogModel, actor: str) -> str:
        """User X removed User Y."""
        return f'{actor} removed {activity.item_name}'

    @staticmethod
    def _twofactor_reset(activity: ActivityLogModel, actor: str) -> str:
        """User X reset passcode for User Y."""
        return f'{actor} reset passcode for {activity.item_name}'

    @staticmethod
    def _payment_info_change(activity: ActivityLogModel, actor: str) -> str:
        """User X updated the account payment information to [payment method]."""
        return f'{actor} updated the account payment information to {activity.item_value}'

    @staticmethod
    def _adding_a_business_affilliation(activity: ActivityLogModel, actor: str) -> str:
        """User X has affiliated [Business Name] to the account."""
        return f'{actor} has affiliated {activity.item_name} to the account'

    @staticmethod
    def _removing_a_business_affilliation(activity: ActivityLogModel, actor: str) -> str:
        """User X has unaffiliated [Business Name] from the account."""
        return f'{actor} has unaffiliated {activity.item_name} from the account'

    @staticmethod
    def _account_name_changes(activity: ActivityLogModel, actor: str) -> str:
        """User X changed the account name to [new account name]."""
        return f'{actor} changed the account name to {activity.item_value}'

    @staticmethod
    def _account_address_changes(activity: ActivityLogModel, actor: str) -> str:
        """User X changed the mailing address to [new mailing address]."""
        return f'{actor} changed the mailing address to {activity.item_value}'

    @staticmethod
    def _authentication_method_changes(activity: ActivityLogModel, actor: str) -> str:
        """User X changed the account authentication method to [auth type]."""
        return f'{actor} changed the account authentication method to {activity.item_value}'

    @staticmethod
    def _account_suspension(activity: ActivityLogModel) -> str:
        """Account was suspended due to [Suspension reason]."""
        return f'The account was suspended due to {activity.item_value}'

    @staticmethod
    def _adding_products_and_services(activity: ActivityLogModel, actor: str) -> str:
        """User X added [product name] to the account Products and Services."""
        return f'{actor} added {activity.item_name} from account Products and Services'

    @staticmethod
    def _removing_products_and_services(activity: ActivityLogModel, actor: str) -> str:
        """User X removed [product name] from the account Products and Services."""
        return f'{actor} removed {activity.item_name} from account Products and Services'

    @staticmethod
    def _mask_user_name(is_staff_access, user):
        is_actor_a_staff = user.type == Role.STAFF.name
        if not is_staff_access and is_actor_a_staff:
            # if staff ,change it to BC Regisitry Staff
            actor = 'BC Registry Staff'
        else:
            actor = user.username if is_actor_a_staff else f'{user.firstname} {user.lastname}'
        return actor
