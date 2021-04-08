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
"""API endpoints for managing a Task resource."""

from flask import g, request
from flask_restplus import Namespace, Resource, cors
from auth_api.tracer import Tracer
from auth_api.auth import jwt as _jwt
from auth_api.utils.util import cors_preflight
from auth_api.utils.roles import Role
from auth_api.services import Task as TaskService
from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.schemas import TaskSchema
from auth_api.models import Task as TaskModel
from auth_api.schemas import utils as schema_utils
from auth_api.utils.enums import TaskStatus

API = Namespace('tasks', description='Endpoints for tasks management')
TRACER = Tracer.get_instance()


@cors_preflight('GET,OPTIONS')
@API.route('', methods=['GET', 'OPTIONS'])
class Tasks(Resource):
    """Resource for fetching tasks."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_jwt.has_one_of_roles([Role.STAFF.value])
    def get():
        """Fetch tasks."""
        try:
            # Search based on request arguments
            task_type = request.args.get('type', None)
            task_status = request.args.get('status', TaskStatus.OPEN.value)

            tasks = TaskService.fetch_tasks(task_type=task_type, task_status=task_status)
            response, status = {'tasks': TaskSchema().dump(tasks, many=True)}, http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status


@cors_preflight('PUT,OPTIONS')
@API.route('/<int:task_id>', methods=['PUT', 'OPTIONS'])
class TaskUpdate(Resource):
    """Resource for updating a task."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_jwt.has_one_of_roles([Role.STAFF.value])
    def put(task_id):
        """Update a task."""
        request_json = request.get_json()
        token = g.jwt_oidc_token_info

        valid_format, errors = schema_utils.validate(request_json, 'task_request')
        if not valid_format:
            return {'message': schema_utils.serialize(errors)}, http_status.HTTP_400_BAD_REQUEST

        try:
            task = TaskService(TaskModel.find_by_task_id(task_id))
            if task:
                # Update task and its relationships
                origin = request.environ.get('HTTP_ORIGIN', 'localhost')
                response, status = task.update_task(task_info=request_json,
                                                    token_info=token,
                                                    origin_url=origin).as_dict(), http_status.HTTP_200_OK

            else:
                response, status = {'message': 'The requested task could not be found.'}, \
                                   http_status.HTTP_404_NOT_FOUND

        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status
