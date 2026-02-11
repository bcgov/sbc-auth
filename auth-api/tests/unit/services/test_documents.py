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

"""Tests to verify the User Service.

Test-Suite to ensure that the Document Service is working as expected.
"""

from auth_api.models import Documents as DocumentsModel
from auth_api.services import Documents as DocumentService
from tests.utilities.factory_utils import get_tos_latest_version


def test_as_dict(session):  # pylint: disable=unused-argument
    """Assert that a document is rendered correctly as a dictionary."""
    _model = DocumentsModel.fetch_latest_document_by_type("termsofuse")
    termsofuse = DocumentService(_model)
    dictionary = termsofuse.as_dict()
    assert dictionary["type"] == "termsofuse"


def test_with_valid_type(session):  # pylint: disable=unused-argument
    """Assert that a document is rendered correctly as a dictionary."""
    terms_of_use = DocumentService.fetch_latest_document("termsofuse")
    assert terms_of_use is not None


def test_with_no_valid_type(session):  # pylint: disable=unused-argument
    """Assert that a document is rendered correctly as a dictionary."""
    terms_of_use = DocumentService.fetch_latest_document("sometype")
    assert terms_of_use is None


def test_find_latest_version_by_invalid_type(session):  # pylint: disable=unused-argument
    """Assert that a document is rendered correctly as a dictionary."""
    terms_of_use = DocumentService.find_latest_version_by_type("sometype")
    assert terms_of_use is None


def test_find_latest_version_by_type(session):  # pylint: disable=unused-argument
    """Assert that a document is rendered correctly as a dictionary."""
    terms_of_use = DocumentService.find_latest_version_by_type("termsofuse")
    assert terms_of_use == get_tos_latest_version()

