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

    REFUND_DIRECT_PAY_REQUEST = 'bc.registry.payment.direct_pay.refundRequest'
    REFUND_DRAWDOWN_REQUEST = 'bc.registry.payment.drawdown.refundRequest'
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
    EJV_FAILED = 'bc.registry.payment.ejvFailed'
    RESET_PASSCODE = 'bc.registry.auth.resetPasscode'
    ADMIN_NOTIFICATION = 'bc.registry.auth.adminNotification'
    AFFILIATION_INVITATION = 'bc.registry.auth.affiliationInvitation'
    BUSINESS_INVITATION = 'bc.registry.auth.businessInvitation'
    BUSINESS_INVITATION_FOR_BCEID = 'bc.registry.auth.businessInvitationForBceid'
    DIRSEARCH_BUSINESS_INVITATION = 'bc.registry.auth.dirsearchBusinessInvitation'
    GOVM_BUSINESS_INVITATION = 'bc.registry.auth.govmBusinessInvitation'
    GOVM_MEMBER_INVITATION = 'bc.registry.auth.govmMemberInvitation'
    MEMBERSHIP_APPROVED_NOTIFICATION = 'bc.registry.auth.membershipApprovedNotification'
    MEMBERSHIP_APPROVED_NOTIFICATION_FOR_BCEID = 'bc.registry.auth.membershipApprovedNotificationForBceid'
    NONBCSC_ORG_APPROVED_NOTIFICATION = 'bc.registry.auth.nonbcscOrgApprovedNotification'
    NONBCSC_ORG_REJECTED_NOTIFICATION = 'bc.registry.auth.nonbcscOrgRejectedNotification'
    OTP_AUTHENTICATOR_RESET_NOTIFICATION = 'bc.registry.auth.otpAuthenticatorResetNotification'
    ROLE_CHANGED_NOTIFICATION = 'bc.registry.auth.roleChangedNotification'
    STAFF_REVIEW_ACCOUNT = 'bc.registry.auth.staffReviewAccount'
    GOVM_APPROVED_NOTIFICATION = 'bc.registry.auth.govmApprovedNotification'
    GOVM_REJECTED_NOTIFICATION = 'bc.registry.auth.govmRejectedNotification'
    PROD_PACKAGE_APPROVED_NOTIFICATION = 'bc.registry.auth.prodPackageApprovedNotification'
    PROD_PACKAGE_REJECTED_NOTIFICATION = 'bc.registry.auth.prodPackageRejectedNotification'
    PRODUCT_APPROVED_NOTIFICATION_DETAILED = 'bc.registry.auth.productApprovedNotificationDetailed'
    PRODUCT_REJECTED_NOTIFICATION_DETAILED = 'bc.registry.auth.productRejectedNotificationDetailed'
    RESUBMIT_BCEID_ORG_NOTIFICATION = 'bc.registry.auth.resubmitBceidOrg'
    RESUBMIT_BCEID_ADMIN_NOTIFICATION = 'bc.registry.auth.resubmitBceidAdmin'
    AFFILIATION_INVITATION_REQUEST = 'bc.registry.auth.affiliationInvitationRequest'
    AFFILIATION_INVITATION_REQUEST_AUTHORIZATION = 'bc.registry.auth.affiliationInvitationRequestAuthorization'


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
    NONBCSC_ORG_APPROVED_NOTIFICATION = '[BC Registries and Online Services] APPROVED Business Registry Account'
    NONBCSC_ORG_REJECTED_NOTIFICATION = '[BC Registries and Online Services] YOUR ACTION REQUIRED: ' \
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
    RESUBMIT_BCEID_ORG_NOTIFICATION = '[BC Registries and Online Services] YOUR ACTION REQUIRED: ' \
                                      'Update your information.'
    RESUBMIT_BCEID_ADMIN_NOTIFICATION = '[BC Registries and Online Services] YOUR ACTION REQUIRED: ' \
                                        'Update your information.'
    AFFILIATION_INVITATION_REQUEST = '[BC Registries and Online Services] Request to manage {business_name}'
    AFFILIATION_INVITATION_REQUEST_AUTHORIZATION = '[BC Registries and Online Services] ' \
                                                   'Request to manage {business_name}'


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
    NONBCSC_ORG_APPROVED_NOTIFICATION = 'Your Membership Has Been Approved'
    NONBCSC_ORG_REJECTED_NOTIFICATION = 'Your Membership Has Been Rejected'
    OTP_AUTHENTICATOR_RESET_NOTIFICATION = 'Your Authenticator Has Been Reset'
    ROLE_CHANGED_NOTIFICATION = 'Your Role Has Been Changed'
    STAFF_REVIEW_ACCOUNT = 'Notification from Business Registry'
    GOVM_APPROVED_NOTIFICATION = 'Your BC Registries Account Has Been Approved'
    GOVM_REJECTED_NOTIFICATION = 'Your BC Registries Account Has Been Rejected'
    PROD_PACKAGE_APPROVED_NOTIFICATION = 'Your Product Request Has Been Approved'
    PROD_PACKAGE_REJECTED_NOTIFICATION = 'Your Product Request Has Been Rejected'
    PRODUCT_APPROVED_NOTIFICATION_DETAILED = 'Your Product Request Has Been Approved'
    PRODUCT_REJECTED_NOTIFICATION_DETAILED = 'Your Product Request Has Been Rejected'
    RESUBMIT_BCEID_ORG_NOTIFICATION = 'Your Account Creation Request is On hold '
    RESUBMIT_BCEID_ADMIN_NOTIFICATION = 'Your Team Member Request is On hold '
    AFFILIATION_INVITATION = 'Invitation to manage a business with your account.'
    AFFILIATION_INVITATION_REQUEST = 'You have been authorized to manage the business.'
    AFFILIATION_INVITATION_REQUEST_AUTHORIZATION = 'You have been authorized to manage the business.'


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
    NONBCSC_ORG_APPROVED_NOTIFICATION_TEMPLATE_NAME = 'nonbcsc_org_approved_notification_email'
    NONBCSC_ORG_REJECTED_NOTIFICATION_TEMPLATE_NAME = 'nonbcsc_org_rejected_notification_email'
    OTP_AUTHENTICATOR_RESET_NOTIFICATION_TEMPLATE_NAME = 'otp_authenticator_reset_notification_email'
    ROLE_CHANGED_NOTIFICATION_TEMPLATE_NAME = 'role_changed_notification_email'
    STAFF_REVIEW_ACCOUNT_TEMPLATE_NAME = 'staff_review_account_email'
    GOVM_APPROVED_NOTIFICATION_TEMPLATE_NAME = 'govm_approved_notification'
    GOVM_REJECTED_NOTIFICATION_TEMPLATE_NAME = 'govm_rejected_notification'
    PROD_PACKAGE_APPROVED_NOTIFICATION_TEMPLATE_NAME = 'prod_package_approved_notification'
    PROD_PACKAGE_REJECTED_NOTIFICATION_TEMPLATE_NAME = 'prod_package_rejected_notification'
    PRODUCT_APPROVED_NOTIFICATION_DETAILED_TEMPLATE_NAME = 'product_approved_notification_detailed'
    PRODUCT_REJECTED_NOTIFICATION_DETAILED_TEMPLATE_NAME = 'product_rejected_notification_detailed'
    RESUBMIT_BCEID_ORG_NOTIFICATION_TEMPLATE_NAME = 'resubmit_bceid_org'
    RESUBMIT_BCEID_ADMIN_NOTIFICATION_TEMPLATE_NAME = 'resubmit_bceid_admin'
    AFFILIATION_INVITATION_REQUEST_TEMPLATE_NAME = 'affiliation_invitation_request'
    AFFILIATION_INVITATION_REQUEST_AUTHORIZATION_TEMPLATE_NAME = 'affiliation_invitation_request_authorization'


class Constants(Enum):
    """Constants."""

    RESET_PASSCODE_HEADER = 'BC Registries have generated a new passcode for your business.'
