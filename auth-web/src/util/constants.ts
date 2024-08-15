/* eslint-disable @typescript-eslint/no-duplicate-enum-values */
export enum SessionStorageKeys {
    KeyCloakToken = 'KEYCLOAK_TOKEN',
    ApiConfigKey = 'AUTH_API_CONFIG',
    BusinessIdentifierKey = 'BUSINESS_ID',
    CurrentAccount = 'CURRENT_ACCOUNT',
    LaunchDarklyFlags = 'LD_FLAGS',
    ExtraProvincialUser = 'EXTRAPROVINCIAL_USER',
    SessionSynced = 'SESSION_SYNCED',
    InvitationToken = 'INV_TOKEN',
    PaginationOptions = 'PAGINATION_OPTIONS',
    ReviewPaginationOptions = 'REVIEW_PAGINATION_OPTIONS',
    InactivePaginationOptions = 'INACTIVE_PAGINATION_OPTIONS',
    PaginationNumberOfItems = 'PAGINATION_NUMBER_OF_ITEMS',
    ReviewPaginationNumberOfItems = 'REVIEW_PAGINATION_NUMBER_OF_ITEMS',
    InactivePaginationNumberOfItems = 'INACTIVE_PAGINATION_NUMBER_OF_ITEMS',
    OrgSearchFilter = 'ORG_SEARCH_FILTER',
    ReviewSearchFilter = 'REV_SEARCH_FILTER',
    InactiveSearchFilter = 'INACTIVE_SEARCH_FILTER',
    ShortNamesSummaryFilter = 'SHORT_NAMES_SUMMARY_FILTER',
    LinkedShortNamesFilter = 'LINKED_SHORT_NAMES_FILTER',
    ShortNamesTabIndex = 'SHORT_NAMES_TAB_INDEX',
    LinkedAccount = 'LINKED_ACCOUNT',
    PendingAccountsSearchFilter = 'PENDING_ACCOUNTS_SEARCH_FILTER',
    RejectedAccountsSearchFilter = 'REJECTED_ACCOUNTS_SEARCH_FILTER',
    InactiveAccountsSearchFilter = 'INACTIVE_ACCOUNTS_SEARCH_FILTER',
    AuthApiUrl = 'AUTH_API_URL',
    AuthWebUrl = 'AUTH_WEB_URL',
    RegistryHomeUrl = 'REGISTRY_HOME_URL',
    StatusApiUrl = 'STATUS_API_URL',
    FasWebUrl = 'FAS_WEB_URL',
    AffidavitNeeded = 'AFFIDAVIT_NEEDED',
    GOVN_USER='AUTH_GOVN_USER',
    NameRequestUrl = 'NAME_REQUEST_URL',
    PprWebUrl = 'PPR_WEB_URL',
    SiteminderLogoutUrl = 'SITEMINDER_LOGOUT_URL',
    PayApiUrl = 'PAY_API_URL'
}

export enum Role {
    AdminEdit = 'admin_edit',
    BnEdit = 'bn_edit',
    Staff = 'staff',
    Public = 'public_user',
    Edit = 'edit',
    Basic = 'basic',
    StaffCreateAccounts = 'create_accounts',
    StaffManageAccounts = 'manage_accounts',
    AnonymousUser = 'anonymous_user',
    StaffViewAccounts = 'view_accounts',
    Tester = 'tester',
    AccountHolder = 'account_holder',
    PublicUser = 'public_user',
    StaffSuspendAccounts = 'suspend_accounts',
    GOVMAccountUser = 'gov_account_user',
    ManageGlCodes = 'manage_gl_codes',
    FasSearch = 'fas_search',
    ViewAllTransactions = 'view_all_transactions',
    ManageEft = 'manage_eft',
    EftRefund = 'eft_refund',
    CreateCredits = 'create_credits',
    FasRefund = 'fas_refund',
    BcolStaffAdmin = 'bcol_staff_admin'
}

export enum Pages {
    USER_PROFILE = 'userprofile',
    CREATE_ACCOUNT = 'setup-account',
    CREATE_GOVM_ACCOUNT = 'setup-govm-account',
    UPDATE_ACCOUNT = 'update-account',
    CREATE_NON_BCSC_ACCOUNT = 'setup-non-bcsc-account',
    CHOOSE_AUTH_METHOD = 'choose-authentication-method',
    PENDING_APPROVAL = 'pendingapproval',
    MAIN = 'account',
    SIGNIN = 'signin',
    SIGNOUT = 'signout',
    CREATE_USER_PROFILE = 'createuserprofile',
    SEARCH_BUSINESS = 'searchbusiness',
    USER_PROFILE_TERMS = 'userprofileterms',
    USER_PROFILE_TERMS_DECLINE = 'unauthorizedtermsdecline',
    HOME = 'home',
    SETUP_ACCOUNT_NON_BCSC = 'nonbcsc-info',
    SETUP_ACCOUNT_NON_BCSC_INSTRUCTIONS = 'instructions',
    SETUP_ACCOUNT_NON_BCSC_DOWNLOAD = 'download',
    ACCOUNT_FREEZE_UNLOCK = 'account-freeze-nsf',
    ACCOUNT_FREEZE = 'account-freeze',
    ACCOUNT_UNLOCK_SUCCESS = 'account-unlock-success',
    ACCOUNT_SETTINGS = 'settings',
    EDIT_ACCOUNT_TYPE= '/change-account',
    STAFF_DASHBOARD_OLD= '/searchbusiness',
    STAFF_SETUP_ACCOUNT = 'staff-setup-account',
    CONFIRM_TOKEN = 'confirmtoken',
    ADMIN = '/admin',
    ADMIN_DASHBOARD = '/admin/dashboard',
    STAFF = '/staff',
    STAFF_DASHBOARD = '/staff/dashboard',
    STAFF_DASHBOARD_ACTIVE = '/staff/dashboard/active',
    STAFF_DASHBOARD_REVIEW = '/staff/dashboard/review',
    STAFF_DASHBOARD_REJECTED = '/staff/dashboard/rejected',
    STAFF_DASHBOARD_INVITATIONS = '/staff/dashboard/invitations',
    STAFF_DASHBOARD_SUSPENDED = '/staff/dashboard/suspended',
    STAFF_DASHBOARD_INACTIVE = '/staff/dashboard/inactive',
    MAKE_CC_PAYMENT = '/make-cc-payment/',
    STAFF_GOVM_SETUP_ACCOUNT = '/staff-govm-setup-account',
    SETUP_GOVM_ACCOUNT_SUCCESS='setup-govm-account-success',
    DUPLICATE_ACCOUNT_WARNING='/duplicate-account-warning',
    AFFIDAVIT_COMPLETE = 'upload-affidavit',
    LOGIN = 'login',
    PAY_OUTSTANDING_BALANCE = 'pay-outstanding-balance',
    PAYMENT_OPTION = 'payment-option'
}

export enum Account {
    // ANONYMOUS = 'ANONYMOUS',
    PREMIUM = 'PREMIUM',
    BASIC = 'BASIC',
    UNLINKED_PREMIUM = 'UNLINKED_PREMIUM', // premium accounts without bcol linking
    STAFF = 'STAFF',
    SBC_STAFF = 'SBC_STAFF'
}

export enum AccountStatus {
    ACTIVE = 'ACTIVE',
    INACTIVE = 'INACTIVE',
    REJECTED = 'REJECTED',
    PENDING_STAFF_REVIEW = 'PENDING_STAFF_REVIEW',
    PENDING_ACTIVATION = 'PENDING_ACTIVATION',
    NSF_SUSPENDED = 'NSF_SUSPENDED',
    SUSPENDED = 'SUSPENDED',
    PENDING_INVITE_ACCEPT = 'PENDING_INVITE_ACCEPT'
}

export enum SuspensionReasonCode {
    OWNER_CHANGE = 'OWNER_CHANGE',
    DISPUTE = 'DISPUTE',
    COURT_ORDER = 'COURT_ORDER',
    FRAUDULENT = 'FRAUDULENT',
    OVERDUE_EFT = 'OVERDUE_EFT'
}

export enum SuspensionReason {
    NSF = 'NSF',
    OVERDUE_EFT = 'Overdue EFT Payments',
    NSF_SUSPENDED = 'NSF SUSPENDED',
    SUSPENDED = 'SUSPENDED'
}

export enum IdpHint {
    BCROS = 'bcros',
    IDIR = 'idir',
    BCSC = 'bcsc',
    BCEID = 'bceid'
}

export enum LoginSource {
    BCROS = 'BCROS',
    IDIR = 'IDIR',
    BCSC = 'BCSC',
    BCEID = 'BCEID'
}

// keep in sync with the pay-api invoice status enum
export enum InvoiceStatus {
    APPROVED = 'APPROVED',
    CANCELLED = 'CANCELLED',
    CREATED = 'CREATED',
    CREDITED = 'CREDITED',
    COMPLETED = 'COMPLETED', // NOTE: this === PAID value (api alters it from PAID to COMPLETED in postdump)
    DELETE_ACCEPTED = 'DELETE_ACCEPTED',
    DELETED = 'DELETED',
    OVERDUE = 'OVERDUE',
    PAID = 'PAID',
    PARTIAL = 'PARTIAL_PAID',
    PENDING = 'PENDING',
    REFUND_REQUESTED = 'REFUND_REQUESTED',
    REFUNDED = 'REFUNDED',
    SETTLEMENT_SCHEDULED = 'SETTLEMENT_SCHED',
    UPDATE_REVENUE_ACCOUNT = 'GL_UPDATED',
    UPDATE_REVENUE_ACCOUNT_REFUND = 'GL_UPDATED_REFUND'
}

export enum AffiliationTypes {
    NAME_REQUEST = 'Name Request',
    AMALGAMATION_APPLICATION = 'Amalgamation Application',
    INCORPORATION_APPLICATION = 'Incorporation Application',
    CONTINUATION_IN = 'Continuation Application',
    CORPORATION = 'Corporation',
    REGISTRATION = 'Registration'
}

export enum LearFilingTypes {
    AMALGAMATION = 'Amalgamation',
    INCORPORATION = 'Incorporation',
    REGISTRATION = 'Registration'
}

// NB: Corp Type is sometimes called Legal Type
// see also https://github.com/bcgov/bcrs-shared-components/blob/main/src/modules/corp-type-module/corp-type-module.ts
export enum CorpTypes {
    // actual corp types

    BC_CCC = 'CC',
    BC_COMPANY = 'BC',
    BC_ULC_COMPANY = 'ULC',

    BENEFIT_COMPANY = 'BEN',
    COOP = 'CP',
    PARTNERSHIP = 'GP',
    SOLE_PROP = 'SP',

    CONTINUE_IN = 'C',
    BEN_CONTINUE_IN = 'CBEN',
    CCC_CONTINUE_IN = 'CCC',
    ULC_CONTINUE_IN = 'CUL',

    // colin
    BC_CORPORATION = 'CR', // SPECIAL NAMEREQUEST-ONLY ENTITY TYPE
    EXTRA_PRO_REG = 'EPR',
    LL_PARTNERSHIP = 'LL',
    LIMITED_CO = 'LLC',
    LIM_PARTNERSHIP = 'LP',
    BC_UNLIMITED = 'UL', // SPECIAL NAMEREQUEST-ONLY ENTITY TYPE
    XPRO_LL_PARTNR = 'XL',
    XPRO_LIM_PARTNR = 'XP',

    // others
    FINANCIAL = 'FI',
    PRIVATE_ACT = 'PA',
    PARISHES = 'PAR',

    // societies
    CONT_IN_SOCIETY = 'CS',
    SOCIETY = 'S',
    XPRO_SOCIETY = 'XS',

    // overloaded values
    AMALGAMATION_APPLICATION = 'ATMP',
    INCORPORATION_APPLICATION = 'TMP',
    CONTINUATION_IN = 'CTMP',
    NAME_REQUEST = 'NR',
    REGISTRATION = 'RTMP'
}

export enum NrState {
    APPROVED = 'APPROVED',
    DRAFT = 'DRAFT',
    HOLD = 'HOLD',
    REJECTED = 'REJECTED',
    CONDITION = 'CONDITION',
    CONDITIONAL = 'CONDITIONAL',
    REFUND_REQUESTED = 'REFUND_REQUESTED',
    CANCELLED = 'CANCELLED',
    EXPIRED = 'EXPIRED',
    CONSUMED = 'CONSUMED',
    PROCESSING = 'PROCESSING',
    INPROGRESS = 'INPROGRESS'
}

export enum NrDisplayStates {
    APPROVED = 'Approved',
    HOLD = 'Pending Staff Review',
    DRAFT = 'Draft',
    REJECTED = 'Rejected',
    CONDITIONAL = 'Conditional Approval',
    REFUND_REQUESTED = 'Cancelled, Refund Requested',
    CANCELLED = 'Cancelled',
    EXPIRED = 'Expired',
    CONSUMED = 'Consumed',
    PROCESSING = 'Processing'
}

export enum NrConditionalStates {
    RECEIVED = 'R',
    WAIVED = 'N',
    REQUIRED = 'Y',
}

export enum NrTargetTypes {
    LEAR = 'lear',
    COLIN = 'colin',
    ONESTOP = 'onestop'
}

export enum NrEntityType {
    // BC Entity Types:
    BC = 'BC', // Benefit Company
    CC = 'CC', // Community Contribution Company
    CP = 'CP', // Cooperative Association
    CR = 'CR', // BC Limited Company
    DBA = 'DBA',
    FI = 'FI',
    FR = 'FR',
    GP = 'GP',
    LL = 'LL',
    LP = 'LP',
    PA = 'PA',
    PAR = 'PAR',
    SO = 'SO',
    UL = 'UL', // Unlimited Liability Company

    // XPRO Entity Types:
    RLC = 'RLC',
    XCP = 'XCP',
    XCR = 'XCR',
    XLL = 'XLL',
    XLP = 'XLP',
    XSO = 'XSO',
    XUL = 'XUL',

    INFO = 'INFO', // special value for sub-menu
}

export enum NrRequestTypeStrings {
  // Alteration
  BECV = 'Alteration', // BC Benefit Company Incorporation
  CSSO = 'Alteration', // Society
  ULBE = 'Alteration', // BC Benefit Company
  ULCR = 'Alteration', // B.C. limited Company
  XCSO = 'Alteration', // Extraprovincial Society

  // Amalgamation
  ASO = 'Amalgamation', // Society
  BEAM = 'Amalgamation', // BC Benefit Company Incorporation
  XCUL = 'Amalgamation', // (Future) Extraprovincial Unlimited Liability Company

  // Assumed Name (not used to display NR type, kept for reference)
  // AL = 'Assumed Name', // Extraprovincial Limited Liability Company
  // AS = 'Assumed Name', // (Future) Extraprovincial Cooperative
  // UA = 'Assumed Name', // (Future) Extraprovincial Unlimited Liability Company
  // XASO = 'Assumed Name', // Extraprovincial Society

  // Change Assumed Name (not used to display NR type, kept for reference)
  // XCASO = 'Change Assumed Name', // Extraprovincial Society

  // Continuation application
  BECT = 'Continuation Application', // BC Benefit Company Incorporation
  CCCT = 'Continuation Application', // Community Contribution Co.
  CT = 'Continuation Application', // B.C. Company
  CTC = 'Continuation Application', // Cooperative
  CTSO = 'Continuation Application', // Society
  ULCT = 'Continuation Application', // Unlimited Liability Co.

  // Conversion
  BECR = 'Conversion (Act)', // BC Benefit Company Incorporation
  CCV = 'Conversion (Act)', // Community Contribution Co.
  UC = 'Conversion (Act)', // Unlimited Liability Co.
  ULCB = 'Conversion (Act)', // Unlimited Liability Co.

  // Incorporation
  BC = 'Incorporation', // BC Benefit Company Incorporation
  CC = 'Incorporation', // Community Contribution Co.
  CP = 'Incorporation', // Cooperative
  CR = 'Incorporation', // B.C. Company
  FI = 'Incorporation', // Financial Institution (BC)
  PA = 'Incorporation', // Private Act
  PAR = 'Incorporation', // Parish
  SO = 'Incorporation', // Society
  UL = 'Incorporation', // Unlimited Liability Co.
  XCR = 'Incorporation', // (Future) Extraprovincial Corporation
  XCP = 'Incorporation', // Extraprovincial Cooperative
  XSO = 'Incorporation', // Extraprovincial Society
  XUL = 'Incorporation', // (Future) Extraprovincial Unlimited Liability Company

  // Name Change
  BEC = 'Name Change', // BC Benefit Company Incorporation
  CCC = 'Name Change', // Community Contribution Co.
  CCP = 'Name Change', // Cooperative
  CCR = 'Name Change', // B.C. Company
  CFI = 'Name Change', // Financial Institution (BC)
  CFR = 'Name Change', // Sole Proprietorship/General Partnership/DBA
  CLC = 'Name Change', // Extraprovincial Limited Liability Company
  CLL = 'Name Change', // Limited Liability Partnership
  CLP = 'Name Change', // Limited Partnership
  CSO = 'Name Change', // Society
  CUL = 'Name Change', // Unlimited Liability Co.
  XCCP = 'Name Change', // Extraprovincial Cooperative
  XCCR = 'Name Change', // (Future) Extraprovincial Corporation
  XCLL = 'Name Change', // Extraprovincial Limited Liability Partnership
  XCLP = 'Name Change', // Extraprovincial Limited Partnership

  // Registration
  FR = 'Registration', // Sole Proprietorship/General Partnership/DBA
  LC = 'Registration', // Extraprovincial Limited Liability Company
  LL = 'Registration', // Limited Liability Partnership
  LP = 'Registration', // Limited Partnership
  XLL = 'Registration', // Extraprovincial Limited Liability Partnership
  XLP = 'Registration', // Extraprovincial Limited Partnership

  // Reinstatement
  RLC = 'Reinstatement', // Extraprovincial Limited Liability Company
  XRCR = 'Reinstatement', // (Future) Extraprovincial Corporation

  // Restoration
  BERE = 'Restoration', // BC Benefit Company Incorporation
  RCC = 'Restoration', // Community Contribution Co.
  RCP = 'Restoration', // Cooperative
  RCR = 'Restoration', // B.C. Company
  RFI = 'Restoration', // Financial Institution (BC)
  RSO = 'Restoration', // Society
  RUL = 'Restoration', // Unlimited Liability Co.
  XRCP = 'Restoration', // Extraprovincial Cooperative
  XRSO = 'Restoration', // Extraprovincial Society
  XRUL = 'Restoration' // (Future) Extraprovincial Unlimited Liability Company
}

export enum BusinessState {
    ACTIVE = 'Active',
    APPROVED = 'Approved',
    DRAFT = 'Draft',
    AWAITING_REVIEW = 'Pending Staff Review',
    CHANGE_REQUESTED = 'Change Requested',
    REJECTED = 'Rejected',
    HISTORICAL = 'Historical',
    PENDING = 'Pending | Payment Incomplete',
    PAID = 'Filed and Pending', // Paid and the Filer hasn't processed yet, or overdue FE
    PAID_FE = 'Future Effective' // Paid and FE

}

export enum AccessType {
    REGULAR = 'REGULAR',
    EXTRA_PROVINCIAL = 'EXTRA_PROVINCIAL',
    ANONYMOUS = 'ANONYMOUS',
    REGULAR_BCEID = 'REGULAR_BCEID',
    GOVM = 'GOVM',
    GOVN = 'GOVN'
}

export enum Permission {
    REMOVE_BUSINESS = 'REMOVE_BUSINESS',
    CHANGE_ADDRESS = 'CHANGE_ADDRESS',
    VIEW_ADDRESS = 'VIEW_ADDRESS',
    CHANGE_ORG_NAME = 'CHANGE_ORG_NAME',
    INVITE_MEMBERS = 'INVITE_MEMBERS',
    CHANGE_ACCOUNT_TYPE = 'CHANGE_ACCOUNT_TYPE',
    CHANGE_ROLE = 'CHANGE_ROLE',
    RESET_PASSWORD = 'RESET_PASSWORD',
    VIEW_ACCOUNT = 'VIEW_ACCOUNT',
    TRANSACTION_HISTORY = 'TRANSACTION_HISTORY',
    MANAGE_STATEMENTS = 'MANAGE_STATEMENTS',
    VIEW_PAYMENT_METHODS = 'VIEW_PAYMENT_METHODS',
    VIEW_ADMIN_CONTACT = 'VIEW_ADMIN_CONTACT',
    RESET_OTP = 'RESET_OTP',
    MAKE_PAYMENT = 'MAKE_PAYMENT',
    GENERATE_INVOICE = 'GENERATE_INVOICE',
    VIEW_AUTH_OPTIONS = 'VIEW_AUTH_OPTIONS',
    CHANGE_AUTH_OPTIONS = 'CHANGE_AUTH_OPTIONS',
    EDIT_REQUEST_PRODUCT_PACKAGE = 'EDIT_REQUEST_PRODUCT_PACKAGE',
    VIEW_ACTIVITYLOG = 'VIEW_ACTIVITYLOG',
    VIEW_REQUEST_PRODUCT_PACKAGE='VIEW_REQUEST_PRODUCT_PACKAGE',
    DEACTIVATE_ACCOUNT='DEACTIVATE_ACCOUNT',
    VIEW_USER_LOGINSOURCE='VIEW_USER_LOGINSOURCE',
    EDIT_BUSINESS_INFO = 'EDIT_BUSINESS_INFO',
    VIEW_DEVELOPER_ACCESS = 'VIEW_DEVELOPER_ACCESS',
}

export enum LDFlags {
    AlternateNamesMbr = 'enable-alternate-names-mbr',
    AffiliationInvitationRequestAccess = 'enable-affiliation-invitation-request-access',
    BannerText = 'banner-text',
    BusSearchLink = 'bus-search-staff-link',
    EnableBcCccUlc = 'enable-bc-ccc-ulc',
    EnableBusinessNrSearch = 'enable-business-nr-search',
    EnableDetailsFilter = 'enable-transactions-detail-filter',
    EnableEFTPaymentMethod = 'enable-eft-payment-method',
    EnableInvoluntaryDissolution = 'enable-involuntary-dissolution',
    IaSupportedEntities = 'ia-supported-entities',
    ProductBCAStatus = 'product-BCA-status',
    ProductBusSearchPremTooltip = 'product-BUSINESS_SEARCH-prem-tooltip',
    ProductBusSearchStatus = 'product-BUSINESS_SEARCH-status',
    ProductCSOStatus = 'product-CSO-status',
    ProductSiteRegistryStatus = 'product-ESRA-status',
    ProductWillsStatus = 'product-VS-status',
    SupportedAmalgamationEntities = 'supported-amalgamation-entities',
    SupportedContinuationInEntities = 'supported-continuation-in-entities',
    SentryEnable = 'sentry-enable',
    SupportRestorationEntities = 'supported-restoration-entities',
    AllowableBusinessSearchTypes = 'allowable-business-search-types',
    AllowableBusinessPasscodeTypes = 'allowable-business-passcode-types',
    EnableAffiliationDelegation = 'enable-affiliation-delegation',
    EnableCreditCardPremium = 'enable-credit-card-premium',
    EnableEFTBalanceByPAD = 'enable-eft-balance-by-pad',
}

export enum DateFilterCodes {
    TODAY = 'TODAY',
    YESTERDAY = 'YESTERDAY',
    LASTWEEK = 'LASTWEEK',
    LASTMONTH = 'LASTMONTH',
    CUSTOMRANGE = 'CUSTOMRANGE'
}

export enum SearchFilterCodes {
    DATERANGE = 'daterange',
    USERNAME = 'username',
    ACCOUNTNAME = 'accountname',
    FOLIONUMBER = 'folio'
}

export enum PaymentTypes {
    CASH = 'CASH',
    CHEQUE = 'CHEQUE',
    CREDIT_CARD = 'CC',
    BCOL = 'DRAWDOWN',
    DIRECT_PAY = 'DIRECT_PAY',
    EFT = 'EFT',
    INTERNAL = 'INTERNAL',
    NO_FEE = 'NO_FEE',
    ONLINE_BANKING = 'ONLINE_BANKING',
    PAD = 'PAD',
    EJV = 'EJV',
    WIRE = 'WIRE'
}

export enum paymentErrorType {
    GENERIC_ERROR = 'GENERIC_ERROR',
    PAYMENT_CANCELLED = 'PAYMENT_CANCELLED',
    DECLINED= 'DECLINED',
    INVALID_CARD_NUMBER = 'INVALID_CARD_NUMBER',
    DECLINED_EXPIRED_CARD = 'DECLINED_EXPIRED_CARD',
    DUPLICATE_ORDER_NUMBER = 'DUPLICATE_ORDER_NUMBER',
    TRANSACTION_TIMEOUT_NO_DEVICE = 'TRANSACTION_TIMEOUT_NO_DEVICE',
    VALIDATION_ERROR = 'VALIDATION_ERROR',
}

export enum StaffCreateAccountsTypes {
    DIRECTOR_SEARCH = 'DIRECTOR_SEARCH',
    GOVM_BUSINESS = 'GOVM_BUSINESS'
}

export enum ProductStatus {
    NOT_SUBSCRIBED = 'NOT_SUBSCRIBED',
    PENDING_STAFF_REVIEW = 'PENDING_STAFF_REVIEW',
    ACTIVE = 'ACTIVE',
    REJECTED = 'REJECTED',
}

export enum TaskRelationshipType {
    ORG = 'ORG',
    PRODUCT = 'PRODUCT',
    USER = 'USER'
}

export enum TaskRelationshipStatus {
    ACTIVE = 'ACTIVE',
    INACTIVE = 'INACTIVE',
    REJECTED = 'REJECTED',
    PENDING_STAFF_REVIEW = 'PENDING_STAFF_REVIEW',
    PENDING_ACTIVATION = 'PENDING_ACTIVATION',
    PENDING_INVITE_ACCEPT = 'PENDING_INVITE_ACCEPT',
    HOLD = 'HOLD'
}

export enum TaskStatus {
    OPEN = 'OPEN',
    COMPLETED = 'COMPLETED',
    HOLD = 'HOLD'
}

export enum TaskType {
    NEW_ACCOUNT_STAFF_REVIEW = 'New Account',
    GOVM_REVIEW = 'GovM',
    GOVN_REVIEW = 'GovN',
    BCEID_ADMIN_REVIEW = 'BCeID Admin',
    MHR_LAWYER_NOTARY = 'Manufactured Home Registry – Lawyers and Notaries',
    MHR_MANUFACTURERS = 'Manufactured Home Registry – Manufacturers',
    MHR_DEALERS = 'Manufactured Home Registry – Home Dealers'
}

export enum TaskAction {
    AFFIDAVIT_REVIEW = 'AFFIDAVIT_REVIEW',
    ACCOUNT_REVIEW = 'ACCOUNT_REVIEW',
    PRODUCT_REVIEW = 'PRODUCT_REVIEW'
}

export enum FeeCodes {
    PPR_CHANGE_OR_AMENDMENT = 'TRF'
}

export enum DisplayModeValues{
    VIEW_ONLY = 'VIEW_ONLY'
}

export enum OnholdOrRejectCode {
    ONHOLD = 'On Hold',
    REJECTED = 'Reject Account'
}

export const ORG_AUTO_COMPLETE_MAX_RESULTS_COUNT = 5
export const ALLOWED_URIS_FOR_PENDING_ORGS: string[] = ['setup-non-bcsc-account', 'signout']

export const DEACTIVATE_ACCOUNT_MESSAGE : Map<string, string> = new Map([
  ['OUTSTANDING_CREDIT', 'deactivateCreditAccountMsg'],
  ['TRANSACTIONS_IN_PROGRESS', 'deactivateActiveTransactionsMsg'],
  ['DEFAULT', 'deactivateGenericMsg']
])

export enum AffidavitStatus {
    PENDING = 'PENDING',
    APPROVED = 'APPROVED',
    REJECTED = 'REJECTED',
    INACTIVE = 'INACTIVE'
}

export enum AffidavitNumberStatus {
    PENDING = 'Pending'
}

export enum PatchActions {
    UPDATE_STATUS = 'updateStatus',
    UPDATE_ACCESS_TYPE = 'updateAccessType'
}

export enum RequestTrackerType {
    InformCRA = 'INFORM_CRA',
    ChangeDeliveryAddress = 'CHANGE_DELIVERY_ADDRESS',
    ChangeMailingAddress = 'CHANGE_MAILING_ADDRESS',
    ChangeName = 'CHANGE_NAME',
    ChangeStatus = 'CHANGE_STATUS',
    ChangeParty = 'CHANGE_PARTY',
}

export enum Product {
    BCA = 'BCA',
    BUSINESS = 'BUSINESS',
    BUSINESS_SEARCH = 'BUSINESS_SEARCH',
    CSO = 'CSO',
    ESRA = 'ESRA',
    MHR = 'MHR',
    PPR = 'PPR',
    RPPR = 'RPPR',
    RPT = 'RPT',
    VS = 'VS'
}

export enum EntityAlertTypes {
    FROZEN = 'FROZEN',
    BADSTANDING = 'BAD_STANDING',
    LIQUIDATION = 'LIQUIDATION',
    DISSOLUTION = 'DISSOLUTION',
    PROCESSING = 'PROCESSING',
    EXPIRED = 'EXPIRED'
}

export enum MagicLinkInvitationStatus {
    EXPIRED_AFFILIATION_INVITATION = 'EXPIRED_AFFILIATION_INVITATION',
    ACTIONED_AFFILIATION_INVITATION = 'ACTIONED_AFFILIATION_INVITATION'
}

export enum AffiliationInvitationStatus {
  Pending = 'PENDING',
  Accepted = 'ACCEPTED',
  Expired = 'EXPIRED',
  Failed = 'FAILED'
}

export enum AffiliationInvitationType {
  REQUEST = 'REQUEST',
  EMAIL = 'EMAIL'
}

export enum ShortNameStatus {
    LINKED = 'LINKED',
    UNLINKED = 'UNLINKED',
    PENDING = 'PENDING'
}

export enum ShortNamePaymentActions {
    APPLY_CREDITS = 'APPLY_CREDITS',
    CANCEL = 'CANCEL',
    REVERSE = 'REVERSE'
}

export enum ShortNameReversePaymentErrors {
    INVALID_STATE = 'EFT_PAYMENT_ACTION_CREDIT_LINK_STATUS_INVALID',
    UNPAID_STATEMENT = 'EFT_PAYMENT_ACTION_UNPAID_STATEMENT',
    UNPAID_STATEMENT_INVOICE = 'EFT_PAYMENT_INVOICE_REVERSE_UNEXPECTED_STATUS',
    EXCEEDS_SIXTY_DAYS = 'EFT_PAYMENT_ACTION_REVERSAL_EXCEEDS_SIXTY_DAYS'
}

export enum ShortNameLinkStatus {
    PENDING = 'PENDING',
    LINKED = 'LINKED',
    INACTIVE = 'INACTIVE'
}

export enum ShortNameResponseStatus {
    EFT_SHORT_NAME_ALREADY_MAPPED = 'EFT_SHORT_NAME_ALREADY_MAPPED'
}

export enum ShortNameHistoryType {
    FUNDS_RECEIVED = 'FUNDS_RECEIVED',
    INVOICE_REFUND = 'INVOICE_REFUND',
    STATEMENT_PAID = 'STATEMENT_PAID',
    STATEMENT_REVERSE = 'STATEMENT_REVERSE'
}

export enum ShortNameHistoryTypeDescription {
    FUNDS_RECEIVED = 'Funds Received',
    INVOICE_REFUND = 'Invoice Refund',
    STATEMENT_PAID = 'Statement Paid',
    STATEMENT_REVERSE = 'Payment Reversed'
}

export enum CfsAccountStatus {
    PENDING = 'PENDING',
    PENDING_PAD_ACTIVATION = 'PENDING_PAD_ACTIVATION',
    ACTIVE = 'ACTIVE',
    INACTIVE = 'INACTIVE',
    FREEZE = 'FREEZE'
}

export enum InvoluntaryDissolutionConfigNames {
  DISSOLUTIONS_ON_HOLD = 'DISSOLUTIONS_ON_HOLD',
  DISSOLUTIONS_STAGE_1_SCHEDULE='DISSOLUTIONS_STAGE_1_SCHEDULE',
  DISSOLUTIONS_STAGE_2_SCHEDULE='DISSOLUTIONS_STAGE_2_SCHEDULE',
  DISSOLUTIONS_STAGE_3_SCHEDULE='DISSOLUTIONS_STAGE_3_SCHEDULE',
  DISSOLUTIONS_SUMMARY_EMAIL = 'DISSOLUTIONS_SUMMARY_EMAIL',
  MAX_DISSOLUTIONS_ALLOWED = 'MAX_DISSOLUTIONS_ALLOWED',
  NUM_DISSOLUTIONS_ALLOWED = 'NUM_DISSOLUTIONS_ALLOWED'
}

export enum AccountType {
    BUSINESS = 'business',
    GOVN = 'govn',
    INDIVIDUAL = 'individual'
}

export enum OrgNameLabel {
    GOVM = 'Ministry Name',
    GOVN = 'Government Agency Name',
    BUSINESS = 'Legal Business Name',
    REGULAR = 'Account Name'
}
