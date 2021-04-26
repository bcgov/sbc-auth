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
from typing import Dict

from flask import current_app
from jinja2 import Environment, FileSystemLoader
from sbc_common_components.tracing.service_tracing import ServiceTracing  # noqa: I001

from auth_api.models import ActivityLog as ActivityLogModel
from auth_api.schemas import ActivityLogSchema
from auth_api.services.authorization import check_auth
from auth_api.utils.roles import ADMIN, STAFF

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
    def fetch_activity_logs(org_id: int, token_info: Dict = None, **kwargs):
        """Search all activity logs."""
        item_name = kwargs.get('item_name')
        item_type = kwargs.get('item_type')
        action = kwargs.get('action')
        check_auth(token_info, one_of_roles=(ADMIN, STAFF), org_id=org_id)
        logs = {'activity_logs': []}
        page: int = int(kwargs.get('page'))
        limit: int = int(kwargs.get('limit'))
        search_args = (item_name,
                       item_type,
                       action,
                       page,
                       limit)

        current_app.logger.debug('<fetch_activity logs ')
        activity_logs_models, count = ActivityLogModel.fetch_activity_logs_for_account(org_id, *search_args)

        for activity_log in activity_logs_models:
            log_dict = ActivityLog(activity_log).as_dict()
            logs['activity_logs'].append(log_dict)

        logs['total'] = count
        logs['page'] = page
        logs['limit'] = limit

        current_app.logger.debug('>fetch_activiy logs')
        return logs
