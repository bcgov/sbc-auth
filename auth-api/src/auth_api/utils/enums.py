# Copyright © 2024 Province of British Columbia
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


class AuthHeaderType(Enum):
    """Authorization header types."""

    BASIC = 'Basic {}'
    BEARER = 'Bearer {}'


class ContentType(Enum):
    """Http Content Types."""

    JSON = 'application/json'
    FORM_URL_ENCODED = 'application/x-www-form-urlencoded'
    PDF = 'application/pdf'


class NotificationType(Enum):
    """notification types."""

    ROLE_CHANGED = 'ROLE_CHANGED'
    MEMBERSHIP_APPROVED = 'MEMBERSHIP_APPROVED'


class CorpType(Enum):
    """Corp Types."""

    NR = 'NR'
    CP = 'CP'  # Coperative
    TMP = 'TMP'  # Incorporation Application
    CTMP = 'CTMP'  # Continuation In
    RTMP = 'RTMP'  # Registration
    ATMP = 'ATMP'  # Amalgamation
    BC = 'BC'  # Limited Company
    BEN = 'BEN'  # Benefit Company
    ULC = 'ULC'  # Unlimited Liability
    CC = 'CC'  # Community Contribution
    C = 'C'  # Continuation In BC
    CBEN = 'CBEN'  # Continuation In BEN
    CCC = 'CCC'  # Continuation In CC
    CUL = 'CUL'  # Continuation In ULC
    GP = 'GP'  # General Partnership
    SP = 'SP'  # Sole Proprietorship


class ProductTypeCode(Enum):
    """Product Type code."""

    INTERNAL = 'INTERNAL'
    PARTNER = 'PARTNER'


class RequiredAction(Enum):
    """Keycloak required actions."""

    VERIFY_EMAIL = 'VERIFY_EMAIL'
    UPDATE_PROFILE = 'UPDATE_PROFILE'
    CONFIGURE_TOTP = 'CONFIGURE_TOTP'
    UPDATE_PASSWORD = 'UPDATE_PASSWORD'


class PaymentMethod(Enum):
    """Payment types."""

    CREDIT_CARD = 'CC'
    BCOL = 'DRAWDOWN'
    DIRECT_PAY = 'DIRECT_PAY'
    ONLINE_BANKING = 'ONLINE_BANKING'
    PAD = 'PAD'
    EJV = 'EJV'
    EFT = 'EFT'


class PaymentAccountStatus(Enum):
    """Payment types."""

    CREATED = 'CREATED'
    PENDING = 'PENDING'
    FAILED = 'FAILED'


class OrgType(Enum):
    """Org types."""

    PREMIUM = 'PREMIUM'
    BASIC = 'BASIC'
    STAFF = 'STAFF'
    SBC_STAFF = 'SBC_STAFF'


class DocumentType(Enum):
    """Document types."""

    TERMS_OF_USE = 'termsofuse'
    TERMS_OF_USE_DIRECTOR_SEARCH = 'termsofuse_directorsearch'
    TERMS_OF_USE_GOVM = 'termsofuse_govm'
    AFFIDAVIT = 'affidavit'
    TERMS_OF_USE_PAD = 'termsofuse_pad'


class NRStatus(Enum):
    """NR statuses."""

    APPROVED = 'APPROVED'
    CONDITIONAL = 'CONDITIONAL'
    DRAFT = 'DRAFT'
    CONSUMED = 'CONSUMED'
    INPROGRESS = 'INPROGRESS'


class NRNameStatus(Enum):
    """NR name statuses."""

    APPROVED = 'APPROVED'
    CONDITION = 'CONDITION'


class AffidavitStatus(Enum):
    """Affidavit statuses."""

    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    INACTIVE = 'INACTIVE'


class AccessType(Enum):
    """Access Types."""

    REGULAR = 'REGULAR'
    REGULAR_BCEID = 'REGULAR_BCEID'
    EXTRA_PROVINCIAL = 'EXTRA_PROVINCIAL'
    ANONYMOUS = 'ANONYMOUS'
    GOVM = 'GOVM'  # for govt ministry
    GOVN = 'GOVN'  # for govt non-ministry


class Status(Enum):
    """User Membership status."""

    ACTIVE = 1
    INACTIVE = 2
    REJECTED = 3
    PENDING_APPROVAL = 4
    PENDING_STAFF_REVIEW = 5


class UserStatus(Enum):
    """User Membership status."""

    ACTIVE = 1
    INACTIVE = 2


class OrgStatus(Enum):
    """User Membership status."""

    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    REJECTED = 'REJECTED'
    PENDING_ACTIVATION = 'PENDING_ACTIVATION'
    NSF_SUSPENDED = 'NSF_SUSPENDED'
    SUSPENDED = 'SUSPENDED'  # this is basically staff suspended for now
    PENDING_INVITE_ACCEPT = 'PENDING_INVITE_ACCEPT'  # staff invited user and waiting for account creation from user.
    PENDING_STAFF_REVIEW = 'PENDING_STAFF_REVIEW'  # user created , staff need to approve.


class ProductSubscriptionStatus(Enum):
    """Product Subscription status."""

    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    REJECTED = 'REJECTED'
    PENDING_STAFF_REVIEW = 'PENDING_STAFF_REVIEW'
    NOT_SUBSCRIBED = 'NOT_SUBSCRIBED'
    SUSPENDED = 'SUSPENDED'  # this is basically staff suspended for now


class SuspensionReasonCode(Enum):
    """Suspension Reason Code for suspending an account."""

    OWNER_CHANGE = 'Account Ownership Change'
    DISPUTE = 'Account Ownership Dispute'
    COURT_ORDER = 'Court Order'
    FRAUDULENT = 'Fraudulent Activity'


class InvitationType(Enum):
    """Invitation type."""

    GOVM = 'GOVM'  # Used to indicate an anonymous account invitation
    DIRECTOR_SEARCH = 'DIRECTOR_SEARCH'  # Used to indicate an anonymous account invitation
    STANDARD = 'STANDARD'  # Used to indicate the standard email invite with admin approval


class AffiliationInvitationType(Enum):
    """Affiliation Invitation type."""

    EMAIL = 'EMAIL'
    REQUEST = 'REQUEST'  # Used to indicate an affiliation invitation initiated through Access Request modal

    @classmethod
    def from_value(cls, value):
        """Return instance from value of the enum."""
        return \
            AffiliationInvitationType(value) if value in cls._value2member_map_ else None  # pylint: disable=no-member


class IdpHint(Enum):
    """IdpHint for user login."""

    BCROS = 'bcros'
    BCEID = 'bceid'


class InvitationStatus(Enum):
    """Invitation statuses."""

    ACCEPTED = 'ACCEPTED'
    PENDING = 'PENDING'
    EXPIRED = 'EXPIRED'
    FAILED = 'FAILED'


class LoginSource(Enum):
    """Login source values."""

    PASSCODE = 'PASSCODE'
    BCSC = 'BCSC'
    BCEID = 'BCEID'
    STAFF = 'IDIR'
    BCROS = 'BCROS'
    API_GW = 'API_GW'
    IDIR = 'IDIR'


class ProductCode(Enum):
    """Product code."""

    BUSINESS = 'BUSINESS'
    BUSINESS_SEARCH = 'BUSINESS_SEARCH'
    VS = 'VS'
    BCA = 'BCA'
    PPR = 'PPR'
    DIR_SEARCH = 'DIR_SEARCH'
    NAMES_REQUEST = 'NRO'
    MHR = 'MHR'
    MHR_QSLN = 'MHR_QSLN'  # Qualified Supplier - Lawyers and Notaries
    MHR_QSHM = 'MHR_QSHM'  # Qualified Supplier - Home Manufacturers
    MHR_QSHD = 'MHR_QSHD'  # Qualified Supplier - Home Dealers
    NDS = 'NDS'


class TaskRelationshipType(Enum):
    """Task relationship type."""

    ORG = 'ORG'  # Task related to Org staff review
    AFFIDAVIT = 'AFFIDAVIT'
    PRODUCT = 'PRODUCT'
    USER = 'USER'


class TaskStatus(Enum):
    """Task relationship type."""

    OPEN = 'OPEN'  # Open Task - needs to be taken action
    COMPLETED = 'COMPLETED'  # Task has been acted upon
    HOLD = 'HOLD'
    CLOSED = 'CLOSED'


class TaskRelationshipStatus(Enum):
    """Task Relationship status."""

    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    REJECTED = 'REJECTED'
    PENDING_ACTIVATION = 'PENDING_ACTIVATION'
    NSF_SUSPENDED = 'NSF_SUSPENDED'
    SUSPENDED = 'SUSPENDED'  # this is basically staff suspended for now
    PENDING_INVITE_ACCEPT = 'PENDING_INVITE_ACCEPT'  # staff invited user and waiting for account creation from user.
    PENDING_STAFF_REVIEW = 'PENDING_STAFF_REVIEW'  # user created , staff need to approve.


class TaskTypePrefix(Enum):
    """Task Type prefix to be appended to type column while saving a task."""

    NEW_ACCOUNT_STAFF_REVIEW = 'New Account'
    GOVM_REVIEW = 'GovM'
    BCEID_ADMIN = 'BCeID Admin'
    GOVN_REVIEW = 'GovN'


class TaskAction(Enum):
    """Task action."""

    AFFIDAVIT_REVIEW = 'AFFIDAVIT_REVIEW'
    ACCOUNT_REVIEW = 'ACCOUNT_REVIEW'
    PRODUCT_REVIEW = 'PRODUCT_REVIEW'
    QUALIFIED_SUPPLIER_REVIEW = 'QUALIFIED_SUPPLIER_REVIEW'


class ActivityAction(Enum):
    """Different actions in an activity."""

    INVITE_TEAM_MEMBER = 'INVITE_TEAM_MEMBER'
    APPROVE_TEAM_MEMBER = 'APPROVE_TEAM_MEMBER'
    REMOVE_TEAM_MEMBER = 'REMOVE_TEAM_MEMBER'
    RESET_2FA = 'RESET_2FA'
    PAYMENT_INFO_CHANGE = 'PAYMENT_INFO_CHANGE'
    CREATE_AFFILIATION = 'CREATE_AFFILIATION'
    REMOVE_AFFILIATION = 'REMOVE_AFFILIATION'
    ACCOUNT_NAME_CHANGE = 'ACCOUNT_NAME_CHANGE'
    ACCOUNT_ADDRESS_CHANGE = 'ACCOUNT_ADDRESS_CHANGE'
    AUTHENTICATION_METHOD_CHANGE = 'AUTHENTICATION_METHOD_CHANGE'
    ACCOUNT_SUSPENSION = 'ACCOUNT_SUSPENSION'
    ADD_PRODUCT_AND_SERVICE = 'ADD_PRODUCT_AND_SERVICE'


class PatchActions(Enum):
    """Patch Actions."""

    UPDATE_STATUS = 'updateStatus'
    UPDATE_ACCESS_TYPE = 'updateAccessType'
    UPDATE_API_ACCESS = 'updateApiAccess'

    @classmethod
    def from_value(cls, value):
        """Return instance from value of the enum."""
        return PatchActions(value) if value in cls._value2member_map_ else None  # pylint: disable=no-member


class KeycloakGroupActions(Enum):
    """Keycloak group actions."""

    ADD_TO_GROUP = 'ADD_TO_GROUP'
    REMOVE_FROM_GROUP = 'REMOVE_FROM_GROUP'


class NRActionCodes(Enum):
    """Name Request Action Codes."""

    AMALGAMATE = 'AML'
    ASSUMED = 'ASSUMED'  # FUTURE: should be AS (as in LEAR)?
    CHANGE_NAME = 'CHG'
    CONVERSION = 'CNV'  # aka Alteration
    DBA = 'DBA'  # doing business as
    MOVE = 'MVE'  # continuation in
    NEW_BUSINESS = 'NEW'  # incorporate or register
    RESTORE = 'REH'  # restore or reinstate
    RENEW = 'REN'  # restore with new name request
    RESTORATION = 'REST'  # FUTURE: unused? delete?
    RESUBMIT = 'RESUBMIT'  # FUTURE: unused? delete?

class QueueMessageTypes(Enum):
    """Queue MessageTypes."""

    ACCOUNT_CONFIRMATION_PERIOD_OVER = 'bc.registry.payment.confirmationPeriodOver'
    ACCOUNT_MAILER = 'bc.registry.auth.mailer'
    ACTIVITY_LOG = 'bc.registry.auth.activity'
    ADMIN_NOTIFICATION = 'bc.registry.auth.adminNotification'
    ADMIN_REMOVED = 'bc.registry.auth.adminRemoved'
    AFFILIATION_INVITATION = 'bc.registry.auth.affiliationInvitation'
    AFFILIATION_INVITATION_REQUEST = 'bc.registry.auth.affiliationInvitationRequest'
    AFFILIATION_INVITATION_REQUEST_AUTH = 'bc.registry.auth.affiliationInvitationRequestAuthorization'
    BUSINESS_INVITATION = 'bc.registry.auth.businessInvitation'
    BUSINESS_INVITATION_FOR_BCEID = 'bc.registry.auth.businessInvitationForBceid'
    DIRSEARCH_BUSINESS_INVITATION = 'bc.registry.auth.dirsearchBusinessInvitation'
    EFT_AVAILABLE_NOTIFICATION = 'bc.registry.payment.eftAvailableNotification'
    EJV_FAILED = 'bc.registry.payment.ejvFailed'
    GOVM_APPROVED_NOTIFICATION = 'bc.registry.auth.govmApprovedNotification'
    GOVM_BUSINESS_INVITATION = 'bc.registry.auth.govmBusinessInvitation'
    GOVM_MEMBER_INVITATION = 'bc.registry.auth.govmMemberInvitation'
    GOVM_REJECTED_NOTIFICATION = 'bc.registry.auth.govmRejectedNotification'
    MEMBERSHIP_APPROVED_NOTIFICATION = 'bc.registry.auth.membershipApprovedNotification'
    MEMBERSHIP_APPROVED_NOTIFICATION_FOR_BCEID = 'bc.registry.auth.membershipApprovedNotificationForBceid'
    NAMES_EVENT = 'bc.registry.names.events'
    NON_BCSC_ORG_APPROVED = 'bc.registry.auth.nonbcscOrgApprovedNotification'
    NON_BCSC_ORG_REJECTED = 'bc.registry.auth.nonbcscOrgRejectedNotification'
    NSF_LOCK_ACCOUNT = 'bc.registry.payment.lockAccount'
    NSF_UNLOCK_ACCOUNT = 'bc.registry.payment.unlockAccount'
    ONLINE_BANKING_OVER_PAYMENT = 'bc.registry.payment.OverPaid'
    ONLINE_BANKING_PAYMENT = 'bc.registry.payment.Payment'
    ONLINE_BANKING_UNDER_PAYMENT = 'bc.registry.payment.UnderPaid'
    OTP_AUTHENTICATOR_RESET_NOTIFICATION = 'bc.registry.auth.otpAuthenticatorResetNotification'
    PAD_ACCOUNT_CREATE = 'bc.registry.payment.padAccountCreate'
    PAD_INVOICE_CREATED = 'bc.registry.payment.pad.invoiceCreated'
    PAD_SETUP_FAILED = 'bc.registry.payment.PadSetupFailed'
    PAYMENT_DUE_NOTIFICATION = 'bc.registry.payment.statementDueNotification'
    PAYMENT_PENDING = 'bc.registry.payment.ob.outstandingInvoice'
    PAYMENT_REMINDER_NOTIFICATION = 'bc.registry.payment.statementReminderNotification'
    PROD_PACKAGE_APPROVED_NOTIFICATION = 'bc.registry.auth.prodPackageApprovedNotification'
    PROD_PACKAGE_REJECTED_NOTIFICATION = 'bc.registry.auth.prodPackageRejectedNotification'
    PRODUCT_APPROVED_NOTIFICATION_DETAILED = 'bc.registry.auth.productApprovedNotificationDetailed'
    PRODUCT_CONFIRMATION_NOTIFICATION = 'bc.registry.auth.productConfirmationNotification'
    PRODUCT_REJECTED_NOTIFICATION_DETAILED = 'bc.registry.auth.productRejectedNotificationDetailed'
    REFUND_DIRECT_PAY_REQUEST = 'bc.registry.payment.direct_pay.refundRequest'
    REFUND_DRAWDOWN_REQUEST = 'bc.registry.payment.drawdown.refundRequest'
    RESET_PASSCODE = 'bc.registry.auth.resetPasscode'
    RESUBMIT_BCEID_ADMIN_NOTIFICATION = 'bc.registry.auth.resubmitBceidAdmin'
    RESUBMIT_BCEID_ORG_NOTIFICATION = 'bc.registry.auth.resubmitBceidOrg'
    ROLE_CHANGED_NOTIFICATION = 'bc.registry.auth.roleChangedNotification'
    STAFF_REVIEW_ACCOUNT = 'bc.registry.auth.staffReviewAccount'
    STATEMENT_NOTIFICATION = 'bc.registry.payment.statementNotification'
    TEAM_MEMBER_INVITED = 'bc.registry.auth.teamMemberInvited'
    TEAM_MODIFIED = 'bc.registry.auth.teamModified'
