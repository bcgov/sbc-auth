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
"""API endpoints for managing an Invitation resource."""
from datetime import datetime

from flask import g
from flask_restx import Namespace, Resource, cors

from auth_api import status as http_status
from auth_api.auth import jwt as _jwt
from auth_api.exceptions import BusinessException
from auth_api.services import Documents as DocumentService
from auth_api.services.minio import MinioService
from auth_api.tracer import Tracer
from auth_api.utils.enums import AccessType, DocumentType, LoginSource
from auth_api.utils.util import cors_preflight


API = Namespace('documents', description='Endpoints for document management')
TRACER = Tracer.get_instance()


@cors_preflight('GET,OPTIONS')
@API.route('/<string:document_type>', methods=['GET', 'OPTIONS'])
class Documents(Resource):
    """Resource for managing Terms Of Use."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_jwt.requires_auth
    def get(document_type):
        """Return the latest terms of use."""
        try:
            if document_type == DocumentType.TERMS_OF_USE.value:
                token = g.jwt_oidc_token_info
                if token.get('accessType', None) == AccessType.ANONYMOUS.value:
                    document_type = DocumentType.TERMS_OF_USE_DIRECTOR_SEARCH.value
                elif token.get('loginSource',
                               None) == LoginSource.STAFF.value:  # ideally for govm user who logs in with IDIR
                    document_type = DocumentType.TERMS_OF_USE_GOVM.value

            doc = DocumentService.fetch_latest_document(document_type)
            if doc is not None:
                doc_dict = doc.as_dict()
                if document_type == DocumentType.TERMS_OF_USE_PAD.value:
                    replaced_content = Documents._replace_current_date(doc)
                    doc_dict.update({'content': replaced_content})

                response, status = doc_dict, http_status.HTTP_200_OK
            else:
                response, status = {'message': 'The requested invitation could not be found.'}, \
                                   http_status.HTTP_404_NOT_FOUND
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status

    @staticmethod
    def _replace_current_date(doc):
        """Replace any dynamic contents."""
        today = datetime.today()
        replaced_content = doc.as_dict().get('content').replace('Month Day, Year',
                                                                today.strftime('%m/%d/%Y'))
        return replaced_content


@cors_preflight('GET,OPTIONS')
@API.route('/<string:file_name>/signatures', methods=['GET', 'OPTIONS'])
class DocumentSignature(Resource):
    """Resource for managing Terms Of Use."""

    @staticmethod
    @TRACER.trace()
    @cors.crossdomain(origin='*')
    @_jwt.requires_auth
    def get(file_name: str):
        """Return the latest terms of use."""
        try:
            response, status = MinioService.create_signed_put_url(file_name), http_status.HTTP_200_OK
        except BusinessException as exception:
            response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
        return response, status
