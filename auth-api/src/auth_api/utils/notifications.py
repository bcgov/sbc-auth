# Copyright © 2024 Province of British Columbia
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
"""Utility helping with notifications to the mailer."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from auth_api.models import ProductCode as ProductCodeModel
from auth_api.models import ProductSubscription as ProductSubscriptionModel
from auth_api.utils.enums import ProductCode, ProductSubscriptionStatus, QueueMessageTypes

DETAILED_MHR_NOTIFICATIONS = (ProductCode.MHR_QSLN.value,
                              ProductCode.MHR_QSHD.value,
                              ProductCode.MHR_QSHM.value
                              )


@dataclass
class ProductSubscriptionInfo:
    """Used for managing product subscription."""

    is_approved: bool
    product_subscription_id: int
    org_id: int
    task_remarks: Optional[str] = None
    is_hold: Optional[bool] = False
    is_resubmitted: Optional[bool] = False


@dataclass
class ProductNotificationInfo:
    """Used for retrieving product notification configuration."""

    product_model: ProductCodeModel
    product_sub_model: ProductSubscriptionModel
    recipient_emails: Optional[str] = None
    remarks: Optional[str] = None
    is_reapproved: Optional[bool] = False
    is_confirmation: Optional[bool] = False


# e.g [BC Registries and Online Services] Your {{MHR_QUALIFIED_SUPPLIER}} Access Has Been Approved
class ProductSubjectDescriptor(Enum):
    """Notification product subject descriptor."""

    MHR_QUALIFIED_SUPPLIER = 'Manufactured Home Registry Qualified Supplier'


# e.g. You've been approved for {{MHR_QUALIFIED_SUPPLIER}} access to...
class ProductAccessDescriptor(Enum):
    """Notification product access descriptor."""

    MHR_QUALIFIED_SUPPLIER = 'Qualified Supplier'


# e.g. You've been approved for Qualified Supplier access to {{MHR}}.
class ProductCategoryDescriptor(Enum):
    """Notification product category descriptor."""

    MHR = 'the Manufactured Home Registry'


class NotificationAttachmentType(Enum):
    """Notification attachment type."""

    MHR_QS = 'QUALIFIED_SUPPLIER'


def get_product_notification_type(product_notification_info: ProductNotificationInfo):
    """Get the appropriate product notification type."""
    product_model = product_notification_info.product_model
    is_reapproved = product_notification_info.is_reapproved
    is_confirmation = product_notification_info.is_confirmation
    subscription_status_code = product_notification_info.product_sub_model.status_code

    # Use detailed version of product subscription notification templates
    if product_model.code in DETAILED_MHR_NOTIFICATIONS:
        if is_reapproved or subscription_status_code == ProductSubscriptionStatus.ACTIVE.value:
            return QueueMessageTypes.DETAILED_APPROVED_PRODUCT.value

        if subscription_status_code == ProductSubscriptionStatus.REJECTED.value:
            return QueueMessageTypes.DETAILED_REJECTED_PRODUCT.value

        if is_confirmation:
            return QueueMessageTypes.DETAILED_CONFIRMATION_PRODUCT.value

    # Use default product subscription notification templates
    if subscription_status_code == ProductSubscriptionStatus.ACTIVE.value:
        return QueueMessageTypes.DEFAULT_APPROVED_PRODUCT.value

    if subscription_status_code == ProductSubscriptionStatus.REJECTED.value:
        return QueueMessageTypes.DEFAULT_REJECTED_PRODUCT.value

    return None


def get_product_notification_data(product_notification_info: ProductNotificationInfo):
    """Get the appropriate product notification data."""
    product_model = product_notification_info.product_model
    recipient_emails = product_notification_info.recipient_emails
    is_reapproved = product_notification_info.is_reapproved
    is_confirmation = product_notification_info.is_confirmation
    subscription_status_code = product_notification_info.product_sub_model.status_code
    remarks = product_notification_info.remarks

    if product_model.code not in DETAILED_MHR_NOTIFICATIONS:
        return get_default_product_notification_data(product_model, recipient_emails)

    if is_confirmation:
        return get_mhr_qs_confirmation_data(product_model, recipient_emails)

    if is_reapproved or subscription_status_code == ProductSubscriptionStatus.ACTIVE.value:
        return get_mhr_qs_approval_data(product_model, recipient_emails, is_reapproved)

    if subscription_status_code == ProductSubscriptionStatus.REJECTED.value:
        return get_mhr_qs_rejected_data(product_model, recipient_emails, remarks)

    return None


def get_default_product_notification_data(product_model: ProductCodeModel, recipient_emails: str):
    """Get the default product notification data."""
    data = {
        'productName': product_model.description,
        'emailAddresses': recipient_emails
    }
    return data


def get_mhr_qs_approval_data(product_model: ProductCodeModel, recipient_emails: str, is_reapproved: bool = False):
    """Get the mhr qualified supplier product approval notification data."""
    data = {
        'subjectDescriptor': ProductSubjectDescriptor.MHR_QUALIFIED_SUPPLIER.value,
        'productAccessDescriptor': ProductAccessDescriptor.MHR_QUALIFIED_SUPPLIER.value,
        'categoryDescriptor': ProductCategoryDescriptor.MHR.value,
        'isReapproved': is_reapproved,
        'productName': product_model.description,
        'emailAddresses': recipient_emails
    }
    return data


def get_mhr_qs_rejected_data(product_model: ProductCodeModel, recipient_emails: str, reject_reason: str = None):
    """Get the mhr qualified supplier product rejected notification data."""
    data = {
        'subjectDescriptor': ProductSubjectDescriptor.MHR_QUALIFIED_SUPPLIER.value,
        'productAccessDescriptor': ProductAccessDescriptor.MHR_QUALIFIED_SUPPLIER.value,
        'accessDisclaimer': True,
        'categoryDescriptor': ProductCategoryDescriptor.MHR.value,
        'productName': product_model.description,
        'emailAddresses': recipient_emails,
        'remarks': reject_reason,
        'contactType': get_notification_contact_type(product_model.code)
    }
    return data


def get_mhr_qs_confirmation_data(product_model: ProductCodeModel, recipient_emails: str):
    """Get the mhr qualified supplier product confirmation notification data."""
    data = {
        'subjectDescriptor': ProductSubjectDescriptor.MHR_QUALIFIED_SUPPLIER.value,
        'productAccessDescriptor': ProductAccessDescriptor.MHR_QUALIFIED_SUPPLIER.value,
        'categoryDescriptor': ProductCategoryDescriptor.MHR.value,
        'productName': product_model.description,
        'emailAddresses': recipient_emails,
        'contactType': get_notification_contact_type(product_model.code),
        'hasAgreementAttachment': True,
        'attachmentType': NotificationAttachmentType.MHR_QS.value,
    }
    return data


def get_notification_contact_type(product_code: str) -> str:
    """Get the notification contact type for a product."""
    return 'BCOL' if product_code == ProductCode.MHR_QSLN.value else 'BCREG'
