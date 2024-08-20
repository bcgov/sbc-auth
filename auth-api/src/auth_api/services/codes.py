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
import importlib

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models import db
from auth_api.models.base_model import BaseCodeModel


class Codes:
    """Retrieving the codes in DB.

    This service manages retrieving the values from code, type or status tables.
    """

    def __init__(self):
        """Return a code service instance."""

    @staticmethod
    def fetch_data_model(code_type: str = None):
        """Return class reference mapped to table.

        :param table_fullname: String with fullname of table.
        :return: Class reference or None.
        """
        for model_class in db.Model.registry._class_registry.values():  # pylint:disable=protected-access
            if hasattr(model_class, "__table__") and model_class.__table__.fullname == code_type:
                if issubclass(model_class, BaseCodeModel):
                    return model_class

        return None

    @classmethod
    def fetch_codes(cls, code_type: str = None) -> []:
        """Return values from code table."""
        try:
            data: [] = None
            if code_type:
                code_model = Codes.fetch_data_model(code_type.lower())

                if code_model:
                    codes = code_model.query.all()

                    data = []
                    # transform each of entry to a dictionary base on schema.
                    for entry in codes:
                        module_name = f"auth_api.schemas.{entry.__tablename__}"
                        class_name = f"{entry.__class__.__name__}Schema"
                        try:
                            schema = getattr(importlib.import_module(module_name), class_name)
                        except ModuleNotFoundError:
                            schema = getattr(
                                importlib.import_module("auth_api.schemas.basecode_type"), "BaseCodeSchema"
                            )
                        code_schema = schema()
                        data.append(code_schema.dump(entry, many=False))
                return data
            return None
        except Exception as exception:  # NOQA # pylint: disable=broad-except
            raise BusinessException(Error.UNDEFINED_ERROR, exception) from exception
