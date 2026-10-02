# Copyright © 2026 Province of British Columbia
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
"""Service for the API Terms of Use accepted per account before creating API keys."""

from __future__ import annotations

from flask import current_app
from sqlalchemy.exc import IntegrityError

from auth_api.exceptions import BusinessException
from auth_api.exceptions.errors import Error
from auth_api.models.dataclass import Activity
from auth_api.models.db import db
from auth_api.models.documents import Documents as DocumentsModel
from auth_api.models.org import Org as OrgModel
from auth_api.models.org_api_terms_acceptance import OrgApiTermsAcceptance as OrgApiTermsAcceptanceModel
from auth_api.services.activity_log_publisher import ActivityLogPublisher
from auth_api.services.authorization import check_auth
from auth_api.utils.enums import ActivityAction, DocumentType
from auth_api.utils.roles import ADMIN, STAFF


class ApiTerms:
    """Manages acceptance of the API Terms of Use per account and document version."""

    @staticmethod
    def get_status(org_id: int) -> dict:
        """Return whether the org has accepted the latest API terms, with details of its last acceptance."""
        check_auth(one_of_roles=(ADMIN, STAFF), org_id=org_id)
        return ApiTerms._build_status(
            OrgApiTermsAcceptanceModel.find_latest_by_org(org_id),
            ApiTerms._is_accepted(org_id, ApiTerms._latest_version()),
        )

    @staticmethod
    def accept(org_id: int, version_id: str) -> dict:
        """Record the org's acceptance of the given terms version, which must be the latest."""
        check_auth(one_of_roles=(ADMIN,), org_id=org_id)
        latest = ApiTerms._latest_version()
        # Check if accepted version is the latest (in case new version published after user accepted)
        if version_id != latest:
            raise BusinessException(Error.API_TERMS_VERSION_MISMATCH, None)
        accepted = OrgApiTermsAcceptanceModel.find_by_org_and_version(org_id, version_id)
        if not accepted:
            try:
                accepted = OrgApiTermsAcceptanceModel(org_id=org_id, version_id=version_id).save()
            except IntegrityError:
                db.session.rollback()
                accepted = OrgApiTermsAcceptanceModel.find_by_org_and_version(org_id, version_id)
            else:
                ActivityLogPublisher.publish_activity(
                    Activity(
                        org_id=org_id,
                        action=ActivityAction.API_TERMS_ACCEPTED.value,
                        name=OrgModel.find_by_id(org_id).name,
                        value=version_id,
                    )
                )
        return ApiTerms._build_status(accepted, is_accepted=accepted is not None)

    @staticmethod
    def _build_status(accepted: OrgApiTermsAcceptanceModel | None, is_accepted: bool) -> dict:
        return {
            "isAccepted": is_accepted,
            "acceptedVersionId": accepted.version_id if accepted else None,
            "acceptedBy": accepted.created_by.username if accepted and accepted.created_by else None,
            "acceptedOn": accepted.created.isoformat() if accepted and accepted.created else None,
        }

    @staticmethod
    def is_latest_accepted(org_id: int) -> bool:
        """Return True if the org accepted the latest terms."""
        latest = ApiTerms._latest_version()
        if not latest:
            current_app.logger.error("No API Terms of Use document found; API key creation is blocked")
            raise BusinessException(Error.API_TERMS_NOT_FOUND, None)
        return ApiTerms._is_accepted(org_id, latest)

    @staticmethod
    def _is_accepted(org_id: int, latest: str | None) -> bool:
        return bool(latest and OrgApiTermsAcceptanceModel.find_by_org_and_version(org_id, latest))

    @staticmethod
    def _latest_version() -> str | None:
        return DocumentsModel.find_latest_version_by_type(DocumentType.TERMS_OF_USE_API.value)
