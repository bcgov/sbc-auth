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


class SubjectType(Enum):
    """Event Types."""

    NSF_LOCK_ACCOUNT_SUBJECT = '[BC Registries and Online Services] Your account has been suspended'
    NSF_UNLOCK_ACCOUNT_SUBJECT = 'Your Account Was Successfully Restored'
    ACCOUNT_CONF_OVER_SUBJECT = '[BC Registries and Online Services] Your account is now active'
    PAD_INVOICE_CREATED = '[BC Registries and Online Services] Your accounts PAD transaction details'
    ADMIN_REMOVED_SUBJECT = '[BC Registries and Online Services] You have been removed as an administrator'
    TEAM_MODIFIED_SUBJECT = '[BC Registries and Online Services] Change in Team members'
    ONLINE_BANKING_PAYMENT_SUBJECT = '[BC Registries and Online Services] Online Banking payment has been received'
    PAD_SETUP_FAILED = '[BC Registries and Online Services] Your Account is Temporarily Suspended'
    PAYMENT_PENDING = '[BC Registries and Online Services] Payment is now due for pending transaction on your account'
    EJV_FAILED = 'GL disbursement failure for EJV'
    RESET_PASSCODE = 'BC Registries Account Passcode Reset'
    ADMIN_NOTIFICATION = '[BC Registries and Online Services] {user_first_name} {user_last_name} ' \
                         'has responded for the invitation to join the account {account_name}'
    AFFILIATION_INVITATION = '[BC Registries and Online Services] Authorise Access to Manage Your Business'
    BUSINESS_INVITATION = '[BC Registries and Online Services] {user_first_name} {user_last_name} ' \
                          'has invited you to join an account'
    BUSINESS_INVITATION_FOR_BCEID = '[BC Registries and Online Services] {user_first_name} {user_last_name} ' \
                                    'has invited you to join an account'
    DIRSEARCH_BUSINESS_INVITATION = 'Your BC Registries Account has been created'
    GOVM_BUSINESS_INVITATION = '[BC Registries and Online Services] ' \
                               'You’ve been invited to create a BC Registries account'
    GOVM_MEMBER_INVITATION = '[BC Registries and Online Services] You have been added as a team member'
    MEMBERSHIP_APPROVED_NOTIFICATION = '[BC Registries and Online Services] Welcome to the account {account_name}'
    MEMBERSHIP_APPROVED_NOTIFICATION_FOR_BCEID = '[BC Registries and Online Services] Welcome to the account ' \
                                                 '{account_name}'
    NON_BCSC_ORG_APPROVED_NOTIFICATION = '[BC Registries and Online Services] APPROVED Business Registry Account'
    NON_BCSC_ORG_REJECTED_NOTIFICATION = '[BC Registries and Online Services] YOUR ACTION REQUIRED: ' \
                                        'Business Registry Account cannot be approved'
    OTP_AUTHENTICATOR_RESET_NOTIFICATION = '[BC Registries and Online Services] Authenticator Has Been Reset'
    ROLE_CHANGED_NOTIFICATION = '[BC Registries and Online Services] Your Role Has Been Changed'
    STAFF_REVIEW_ACCOUNT = '[BC Registries and Online Services] An out of province account needs to be approved.'
    GOVM_APPROVED_NOTIFICATION = '[BC Registries and Online Services] Your BC Registries Account Has Been Approved'
    GOVM_REJECTED_NOTIFICATION = '[BC Registries and Online Services] Your BC Registries Account {account_name} ' \
                                 'Has Been Rejected'
    PROD_PACKAGE_APPROVED_NOTIFICATION = '[BC Registries and Online Services] Your Product Request ' \
                                         '{product_name} Has Been Approved'
    PROD_PACKAGE_REJECTED_NOTIFICATION = '[BC Registries and Online Services] YOUR ACTION REQUIRED: ' \
                                         'Your Product Request {product_name} Has Been Rejected'
    PRODUCT_APPROVED_NOTIFICATION_DETAILED = '[BC Registries and Online Services] Your {subject_descriptor} ' \
                                             'Access Has Been Approved'
    PRODUCT_REJECTED_NOTIFICATION_DETAILED = '[BC Registries and Online Services] Your {subject_descriptor} ' \
                                             'Access Has Been Rejected'
    PRODUCT_CONFIRMATION_NOTIFICATION = '[BC Registries and Online Services] {subject_descriptor} ' \
                                        'Application Confirmation'
    RESUBMIT_BCEID_ORG_NOTIFICATION = '[BC Registries and Online Services] YOUR ACTION REQUIRED: ' \
                                      'Update your information.'
    RESUBMIT_BCEID_ADMIN_NOTIFICATION = '[BC Registries and Online Services] YOUR ACTION REQUIRED: ' \
                                        'Update your information.'
    AFFILIATION_INVITATION_REQUEST = '[BC Registries and Online Services] Request to manage {business_name}'
    AFFILIATION_INVITATION_REQUEST_AUTHORIZATION = '[BC Registries and Online Services] ' \
                                                   'Request to manage {business_name}'
    STATEMENT_NOTIFICATION = 'Your BC Registries statement is available'
    PAYMENT_REMINDER_NOTIFICATION = 'Your BC Registries payment reminder'
    PAYMENT_DUE_NOTIFICATION = 'Your BC Registries payment is due'
    EFT_AVAILABLE_NOTIFICATION = 'New Payment Method Available'


class TitleType(Enum):
    """Event Title Types."""

    ADMIN_NOTIFICATION = 'Notification from Business Registry'
    BUSINESS_INVITATION = 'Invitation to Join an Account at Business Registry'
    BUSINESS_INVITATION_FOR_BCEID = 'Invitation to Join an Account at Business Registry'
    DIRSEARCH_BUSINESS_INVITATION = 'Invitation to Join an Account at Business Registry'
    GOVM_BUSINESS_INVITATION = 'Invitation to Join an Account at Business Registry'
    GOVM_MEMBER_INVITATION = 'Invitation to Join an Account at Business Registry'
    MEMBERSHIP_APPROVED_NOTIFICATION = 'Your Membership Has Been Approved'
    MEMBERSHIP_APPROVED_NOTIFICATION_FOR_BCEID = 'Your Membership Has Been Approved'
    NON_BCSC_ORG_APPROVED_NOTIFICATION = 'Your Membership Has Been Approved'
    NON_BCSC_ORG_REJECTED_NOTIFICATION = 'Your Membership Has Been Rejected'
    OTP_AUTHENTICATOR_RESET_NOTIFICATION = 'Your Authenticator Has Been Reset'
    ROLE_CHANGED_NOTIFICATION = 'Your Role Has Been Changed'
    STAFF_REVIEW_ACCOUNT = 'Notification from Business Registry'
    GOVM_APPROVED_NOTIFICATION = 'Your BC Registries Account Has Been Approved'
    GOVM_REJECTED_NOTIFICATION = 'Your BC Registries Account Has Been Rejected'
    PROD_PACKAGE_APPROVED_NOTIFICATION = 'Your Product Request Has Been Approved'
    PROD_PACKAGE_REJECTED_NOTIFICATION = 'Your Product Request Has Been Rejected'
    PRODUCT_APPROVED_NOTIFICATION_DETAILED = 'Your Product Request Has Been Approved'
    PRODUCT_REJECTED_NOTIFICATION_DETAILED = 'Your Product Request Has Been Rejected'
    PRODUCT_CONFIRMATION_NOTIFICATION = 'Your Product Request Application Has Been Received'
    RESUBMIT_BCEID_ORG_NOTIFICATION = 'Your Account Creation Request is On hold '
    RESUBMIT_BCEID_ADMIN_NOTIFICATION = 'Your Team Member Request is On hold '
    AFFILIATION_INVITATION = 'Invitation to manage a business with your account.'
    AFFILIATION_INVITATION_REQUEST = 'You have been authorized to manage the business.'
    AFFILIATION_INVITATION_REQUEST_AUTHORIZATION = 'You have been authorized to manage the business.'


class TemplateType(Enum):
    """Template Types."""

    NSF_LOCK_ACCOUNT_TEMPLATE_NAME = 'account_suspended_email'
    NSF_UNLOCK_ACCOUNT_TEMPLATE_NAME = 'account_unlocked_email'
    ACCOUNT_CONF_OVER_TEMPLATE_NAME = 'account_conf_over_email'
    PAD_INVOICE_CREATED_TEMPLATE_NAME = 'pad_invoice_email'
    ADMIN_REMOVED_TEMPLATE_NAME = 'admin_removed_email'
    TEAM_MODIFIED_TEMPLATE_NAME = 'team_modified_email'
    ONLINE_BANKING_PAYMENT_TEMPLATE_NAME = 'online_banking_payment'
    ONLINE_BANKING_OVER_PAYMENT_TEMPLATE_NAME = 'online_banking_over_payment'
    ONLINE_BANKING_UNDER_PAYMENT_TEMPLATE_NAME = 'online_banking_under_payment'
    PAD_SETUP_FAILED_TEMPLATE_NAME = 'pad_setup_failed'
    PAYMENT_PENDING_TEMPLATE_NAME = 'paymanet_pending'
    EJV_FAILED_TEMPLATE_NAME = 'ejv_failed_email'
    RESET_PASSCODE_TEMPLATE_NAME = 'reset_passcode'
    ADMIN_NOTIFICATION_TEMPLATE_NAME = 'admin_notification_email'
    AFFILIATION_INVITATION_TEMPLATE_NAME = 'affiliation_invitation_email'
    BUSINESS_INVITATION_TEMPLATE_NAME = 'business_invitation_email'
    BUSINESS_INVITATION_FOR_BCEID_TEMPLATE_NAME = 'business_invitation_email_for_bceid'
    DIRSEARCH_BUSINESS_INVITATION_TEMPLATE_NAME = 'dirsearch_business_invitation_email'
    GOVM_BUSINESS_INVITATION_TEMPLATE_NAME = 'govm_business_invitation_email'
    GOVM_MEMBER_INVITATION_TEMPLATE_NAME = 'govm_member_invitation_email'
    MEMBERSHIP_APPROVED_NOTIFICATION_TEMPLATE_NAME = 'membership_approved_notification_email'
    MEMBERSHIP_APPROVED_NOTIFICATION_FOR_BCEID_TEMPLATE_NAME = 'membership_approved_notification_email_for_bceid'
    NON_BCSC_ORG_APPROVED_NOTIFICATION_TEMPLATE_NAME = 'nonbcsc_org_approved_notification_email'
    NON_BCSC_ORG_REJECTED_NOTIFICATION_TEMPLATE_NAME = 'nonbcsc_org_rejected_notification_email'
    OTP_AUTHENTICATOR_RESET_NOTIFICATION_TEMPLATE_NAME = 'otp_authenticator_reset_notification_email'
    ROLE_CHANGED_NOTIFICATION_TEMPLATE_NAME = 'role_changed_notification_email'
    STAFF_REVIEW_ACCOUNT_TEMPLATE_NAME = 'staff_review_account_email'
    GOVM_APPROVED_NOTIFICATION_TEMPLATE_NAME = 'govm_approved_notification'
    GOVM_REJECTED_NOTIFICATION_TEMPLATE_NAME = 'govm_rejected_notification'
    PROD_PACKAGE_APPROVED_NOTIFICATION_TEMPLATE_NAME = 'prod_package_approved_notification'
    PROD_PACKAGE_REJECTED_NOTIFICATION_TEMPLATE_NAME = 'prod_package_rejected_notification'
    PRODUCT_APPROVED_NOTIFICATION_DETAILED_TEMPLATE_NAME = 'product_approved_notification_detailed'
    PRODUCT_REJECTED_NOTIFICATION_DETAILED_TEMPLATE_NAME = 'product_rejected_notification_detailed'
    PRODUCT_CONFIRMATION_NOTIFICATION_TEMPLATE_NAME = 'product_confirmation_notification'
    RESUBMIT_BCEID_ORG_NOTIFICATION_TEMPLATE_NAME = 'resubmit_bceid_org'
    RESUBMIT_BCEID_ADMIN_NOTIFICATION_TEMPLATE_NAME = 'resubmit_bceid_admin'
    AFFILIATION_INVITATION_REQUEST_TEMPLATE_NAME = 'affiliation_invitation_request'
    AFFILIATION_INVITATION_REQUEST_AUTHORIZATION_TEMPLATE_NAME = 'affiliation_invitation_request_authorization'
    STATEMENT_NOTIFICATION_TEMPLATE_NAME = 'statement_notification'
    PAYMENT_REMINDER_NOTIFICATION_TEMPLATE_NAME = 'payment_reminder_notification'
    PAYMENT_DUE_NOTIFICATION_TEMPLATE_NAME = 'payment_due_notification'
    EFT_AVAILABLE_NOTIFICATION_TEMPLATE_NAME = 'eft_available_notification'


class Constants(Enum):
    """Constants."""

    RESET_PASSCODE_HEADER = 'BC Registries have generated a new passcode for your business.'


class AttachmentTypes(Enum):
    """Notification Attachment Types."""

    QUALIFIED_SUPPLIER = 'QUALIFIED_SUPPLIER'
