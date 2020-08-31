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

"""Tests to assure the Documents Class.

Test-Suite to ensure that the Documents Class is working as expected.
"""

from auth_api.models import Documents


def test_documents_with_insert(session):
    """Assert that a Documents can be stored in the service.

    Start with a blank document.
    """
    doc_latest = Documents.fetch_latest_document_by_type('termsofuse')
    assert doc_latest.version_id == '3'


def test_documents_with_insert_some_type(session):
    """Assert that a Documents can be stored in the service.

    Start with a blank document.
    """
    html_content = '<HTML>'
    # putting higher numbers so that version number doesnt collide with existing in db
    doc = Documents(version_id=20, type='sometype', content=html_content, content_type='text/html')
    session.add(doc)
    session.commit()

    doc_latest = Documents.fetch_latest_document_by_type('sometype')
    assert doc_latest.content == html_content
