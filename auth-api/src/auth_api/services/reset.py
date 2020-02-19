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
"""Service for reset test data."""
from typing import Dict

from auth_api.models import User as UserModel
from auth_api.models import db
from auth_api.utils.roles import Role


class ResetTestData:  # pylint:disable=too-few-public-methods
    """Cleanup all the data from model by created_by column."""

    def __init__(self):
        """Return a reset test data service instance."""

    @staticmethod
    def reset(token_info: Dict):
        """Cleanup all the data from all tables create by the provided user id."""
        if Role.TESTER.value in token_info.get('realm_access').get('roles'):
            user = UserModel.find_by_jwt_token(token_info)
            if user:
                # TODO need to find a way to avoid using protected function
                for model_class in db.Model._decl_class_registry.values():  # pylint:disable=protected-access
                    if hasattr(model_class, 'created_by_id'):
                        for model in model_class.query.filter_by(created_by_id=user.id).all():
                            model.delete()
                    if hasattr(model_class, 'modified_by_id'):
                        for model in model_class.query.filter_by(modified_by_id=user.id).all():
                            model.delete()

                user.modified_by = None
                user.modified_by_id = None
                db.session.delete(user)
                db.session.commit()
