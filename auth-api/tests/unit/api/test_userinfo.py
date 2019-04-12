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

"""Tests to assure the userinfo end-point.

Test-Suite to ensure that the /userinfo endpoint is working as expected.
"""
from datetime import datetime

from tests.utilities.schema_assertions import assert_valid_schema


def factory_userinfo_model(username,
                           roles):
    """Return a valid user object stamped with the supplied designation."""
    from auth_api.models import User as UserModel
    b = UserModel(username=username,
                  roles=roles,)

    return b


