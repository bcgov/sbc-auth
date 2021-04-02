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

from flask_restplus import Namespace, Resource, cors
from auth_api.tracer import Tracer
from auth_api.jwt_wrapper import JWTWrapper
from auth_api.utils.util import cors_preflight
from auth_api.utils.roles import Role
from auth_api.services import Task as TaskService
from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.schemas import TaskSchema


API = Namespace('tasks', description='Endpoints for tasks management')
TRACER = Tracer.get_instance()
_JWT = JWTWrapper.get_instance()


@cors_preflight('GET,OPTIONS')
@API.route('/<string:task_relationship_type>', methods=['GET', 'POST', 'OPTIONS'])
class Tasks(Resource):
    """Resource for managing tasks."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.has_one_of_roles(
        [Role.STAFF.value])
    def get(task_relationship_type):
        """Fetch tasks."""
        try:
            tasks = TaskService.fetch_tasks(task_relationship_type=task_relationship_type)
            response, status = {'tasks': TaskSchema().dump(tasks, many=True)}, http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status


@cors_preflight('PATCH,OPTIONS')
@API.route('/<int:task_id>', methods=['PATCH', 'OPTIONS'])
class Task(Resource):
    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_JWT.has_one_of_roles([Role.STAFF.value])
    def patch(task_id):
        """Update the invitation specified by the provided id as retried."""
        token = g.jwt_oidc_token_info
        origin = request.environ.get('HTTP_ORIGIN', 'localhost')
        try:
            invitation = InvitationService.find_invitation_by_id(invitation_id, token)
            if invitation is None:
                response, status = {'message': 'The requested invitation could not be found.'}, \
                                   http_status.HTTP_404_NOT_FOUND
            else:
                user = UserService.find_by_jwt_token(token)
                response, status = invitation.update_invitation(user, token, origin).as_dict(), http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status
