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
"""Service for retrieving the codes."""
from sqlalchemy.inspection import inspect

from auth_api.models import db
from auth_api.models.base_model import BaseModel


class CleaningTestData:
    """Cleaning all the test data from model by created_by column."""

    def __init__(self):
        """Return a cleaning service instance."""

    @staticmethod
    def fetch_data_models():
        """Return class reference mapped to table.

        :param table_fullname: String with fullname of table.
        :return: Class reference or None.
        """
        models: [] = []
        for model_class in db.Model._decl_class_registry.values():  # pylint:disable=protected-access
            if hasattr(model_class, 'created_by_id'):
                print('Root Model: {}'.format(model_class))
                thing_relations = inspect(model_class).relationships.items()
                i = inspect(model_class)
                referred_classes = [r.mapper.class_ for r in i.relationships]
                print('    referred_classes: {}'.format(referred_classes))
                for sub in referred_classes:
                    j = inspect(sub)
                    sub_referred_classes = [r1.mapper.class_ for r1 in j.relationships]
                    print('        sub_referred_classes: {}'.format(sub_referred_classes))

                for model in model_class.query.filter_by(created_by_id=120).all():
                    print(model)
                models.append(model_class.__name__)

        return models
