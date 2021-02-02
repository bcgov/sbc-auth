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
"""Enum definitions."""
from enum import Enum


class MessageType(Enum):
    """Event Types."""

    REFUND_REQUEST = 'bc.registry.payment.refundRequest'
    PAD_ACCOUNT_CREATE = 'bc.registry.payment.padAccountCreate'
    NSF_LOCK_ACCOUNT = 'bc.registry.payment.lockAccount'
    NSF_UNLOCK_ACCOUNT = 'bc.registry.payment.unlockAccount'
    ACCOUNT_CONFIRMATION_PERIOD_OVER = 'bc.registry.payment.confirmationPeriodOver'
    PAD_INVOICE_CREATED = 'bc.registry.payment.pad.invoiceCreated'
    ADMIN_REMOVED = 'bc.registry.auth.adminRemoved'
    TEAM_MEMBER_INVITED = 'bc.registry.auth.teamMemberInvited'
    TEAM_MODIFIED = 'bc.registry.auth.teamModified'
    ONLINE_BANKING_OVER_PAYMENT = 'bc.registry.payment.OverPaid'
    ONLINE_BANKING_UNDER_PAYMENT = 'bc.registry.payment.UnderPaid'
    ONLINE_BANKING_PAYMENT = 'bc.registry.payment.Payment'
    PAD_SETUP_FAILED = 'bc.registry.payment.PadSetupFailed'
    PAYMENT_PENDING = 'bc.registry.payment.ob.outstandingInvoice'


class SubjectType(Enum):
    """Event Types."""

    NSF_LOCK_ACCOUNT_SUBJECT = '[BC Registries and Online Services] Your account has been suspended'
    NSF_UNLOCK_ACCOUNT_SUBJECT = '[BC Registries and Online Services] Your account has been reactivated'
    ACCOUNT_CONF_OVER_SUBJECT = '[BC Registries and Online Services] Your account is now active'
    PAD_INVOICE_CREATED = '[BC Registries and Online Services] Your accounts PAD transaction details'
    ADMIN_REMOVED_SUBJECT = '[BC Registries and Online Services] You have been removed as an administrator'
    TEAM_MODIFIED_SUBJECT = '[BC Registries and Online Services] Change in Team members'
    ONLINE_BANKING_PAYMENT_SUBJECT = '[BC Registries and Online Services] Online Banking payment has been received'
    PAD_SETUP_FAILED = '[BC Registries and Online Services] Your Account is Temporarily Suspended'
    PAYMENT_PENDING = '[BC Registries and Online Services] Payment is now due for pending transaction on your account'


class TemplateType(Enum):
    """Template Types."""

    NSF_LOCK_ACCOUNT_TEMPLATE_NAME = 'account_suspended_email'
    NSF_UNLOCK_ACCOUNT_TEMPLATE_NAME = 'account_restored_email'
    ACCOUNT_CONF_OVER_TEMPLATE_NAME = 'account_conf_over_email'
    PAD_INVOICE_CREATED_TEMPLATE_NAME = 'pad_invoice_email'
    ADMIN_REMOVED_TEMPLATE_NAME = 'admin_removed_email'
    TEAM_MODIFIED_TEMPLATE_NAME = 'team_modified_email'
    ONLINE_BANKING_PAYMENT_TEMPLATE_NAME = 'online_banking_payment'
    ONLINE_BANKING_OVER_PAYMENT_TEMPLATE_NAME = 'online_banking_over_payment'
    ONLINE_BANKING_UNDER_PAYMENT_TEMPLATE_NAME = 'online_banking_under_payment'
    PAD_SETUP_FAILED_TEMPLATE_NAME = 'pad_setup_failed'
    PAYMENT_PENDING_TEMPLATE_NAME = 'paymanet_pending'
