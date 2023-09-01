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
"""API endpoints for managing a document resource."""


from flask import Blueprint, send_from_directory
from flask_cors import cross_origin

from auth_api import status as http_status
from auth_api.exceptions import BusinessException
from auth_api.services import Documents as DocumentService
from auth_api.tracer import Tracer
from auth_api.utils.endpoints_enums import EndpointEnum
from auth_api.utils.enums import ContentType, DocumentType


bp = Blueprint('DOCUMENTS_AFFIDAVIT', __name__, url_prefix=f'{EndpointEnum.API_V1.value}/documents/affidavit')
TRACER = Tracer.get_instance()


@bp.route('', methods=['GET', 'OPTIONS'])
@cross_origin(origins='*', methods=['GET'])
@TRACER.trace()
def get_affidavit_document():
    """Return the Affidavit."""
    try:
        doc = DocumentService.fetch_latest_document(DocumentType.AFFIDAVIT.value)
        if doc is None:
            response, status = {'message': 'The requested document could not be found.'},\
                http_status.HTTP_404_NOT_FOUND
        elif doc.as_dict().get('content_type', None) == ContentType.PDF.value:  # pdf has to be served as attachment
            return send_from_directory('static', filename=doc.as_dict()['content'], as_attachment=True)
        else:
            response, status = doc.as_dict(), http_status.HTTP_200_OK
    except BusinessException as exception:
        response, status = {'code': exception.code, 'message': exception.message}, exception.status_code
    return response, status
