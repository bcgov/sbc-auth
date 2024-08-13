# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Model to handle all operations related to Corp type master data."""

from .base_model import BaseCodeModel


class CorpType(BaseCodeModel):  # pylint: disable=too-few-public-methods # Temporarily disable until methods defined
    """This class manages all of the base data about a Corp Type."""

    __tablename__ = "corp_types"

    @classmethod
    def get_default_corp_type(cls):
        """Return the default Corp type for an Org."""
        return cls.query.filter_by(default=True).first()
