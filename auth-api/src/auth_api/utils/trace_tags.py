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

"""Tags define for tracing.

This file manage all tracing tags.
"""


class TraceTags:
    """Manages all tags for tracing. """

    ERROR = 'error'

    HTTP_STATUS_CODE = 'http.status_code'

    NR_NUMBER = 'nr.number'

    USER = 'login.user'

    DATABASE_QUERY = 'database.query'

    DATABASE_QUERY_ANSWER = 'database.answer'
