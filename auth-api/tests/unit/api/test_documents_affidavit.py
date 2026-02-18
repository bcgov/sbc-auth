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

"""Tests to assure the documents API end-point.

Test-Suite to ensure that the /documents/affidavit endpoint is working as expected.
"""

from http import HTTPStatus

from auth_api.utils.enums import ContentType


def test_affidavit_returns_200(client, jwt, session):  # pylint:disable=unused-argument
    """Assert get affidavit documents endpoint returns 200."""
    rv = client.get("/api/v1/documents/affidavit")
    assert rv.headers["Content-Type"] == ContentType.PDF.value
    assert rv.status_code == HTTPStatus.OK
    assert rv.headers["Content-Disposition"] == "attachment; filename=affidavit_v2.pdf"
