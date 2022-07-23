
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
    PaginationNumberOfItems = 'PAGINATION_NUMBER_OF_ITEMS',
    OrgSearchFilter = 'ORG_SEARCH_FILTER',
    AuthApiUrl = 'AUTH_API_URL',
    AuthWebUrl = 'AUTH_WEB_URL',
    RegistryHomeUrl = 'REGISTRY_HOME_URL',
    StatusApiUrl = 'STATUS_API_URL',
    FasWebUrl = 'FAS_WEB_URL',
    AffidavitNeeded = 'AFFIDAVIT_NEEDED',
    GOVN_USER='AUTH_GOVN_USER',
    NameRequestUrl = 'NAME_REQUEST_URL',
    PprWebUrl = 'PPR_WEB_URL',
    SiteminderLogoutUrl = 'SITEMINDER_LOGOUT_URL'
}

export enum Role {
    AdminEdit = 'admin_edit',
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
    FasSearch = 'fas_search'
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
    MAKE_PAD_PAYMENT = '/make-cc-payment/',
    STAFF_GOVM_SETUP_ACCOUNT = '/staff-govm-setup-account',
    SETUP_GOVM_ACCOUNT_SUCCESS='setup-govm-account-success',
    DUPLICATE_ACCOUNT_WARNING='/duplicate-account-warning',
    AFFIDAVIT_COMPLETE = 'upload-affidavit',
    LOGIN = 'login'
}

export enum Account {
    // ANONYMOUS = 'ANONYMOUS',
    PREMIUM = 'PREMIUM',
    BASIC = 'BASIC',
    UNLINKED_PREMIUM = 'UNLINKED_PREMIUM', // premium accounts without bcol linking
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

export enum TransactionStatus {
    COMPLETED = 'Completed',
    PENDING = 'Pending',
    CANCELLED = 'Cancelled'
}

export enum AffiliationTypes {
    NAME_REQUEST ='Name Request',
    INCORPORATION_APPLICATION = 'Incorporation Application',
    CORPORATION = 'Corporation',
    REGISTRATION = 'Registration'
}

export enum FilingTypes {
    INCORPORATION_APPLICATION = 'incorporationApplication',
    REGISTRATION = 'registration'
}

export enum LearFilingTypes {
    AMALGAMATION = 'Amalgamation',
    INCORPORATION = 'Incorporation',
    REGISTRATION = 'Registration'
}

export enum LegalTypes {
    BCOMP = 'BEN',
    COOP = 'CP',
    CORP = 'CR',
    SP = 'SP',
    GP = 'GP'
}

export enum CorpType {
    COOP = 'CP',
    NEW_BUSINESS = 'TMP',
    NEW_REGISTRATION = 'RTMP',
    BCOMP = 'BEN',
    NAME_REQUEST = 'NR',
    TEMP = 'TMP'
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
    EXPIRED = 'EXPIRED'
}

export enum NrDisplayStates {
    APPROVED = 'Approved',
    HOLD = 'Pending Staff Review',
    DRAFT = 'Pending Staff Review',
    REJECTED = 'Rejected',
    CONDITIONAL = 'Conditional Approval',
    REFUND_REQUESTED = 'Cancelled, Refund Requested',
    CANCELLED = 'Cancelled',
    EXPIRED = 'Expired'
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
    FR = 'FR',
    DBA = 'DBA',
    CR = 'CR',
    UL = 'UL',
    GP = 'GP',
    LP = 'LP',
    LL = 'LL',
    CP = 'CP',
    BC = 'BC',
    CC = 'CC',
    SO = 'SO',
    PA = 'PA',
    FI = 'FI',
    PAR = 'PAR',

    // XPRO Entity Types:
    XCR = 'XCR',
    XUL = 'XUL',
    RLC = 'RLC',
    XLP = 'XLP',
    XLL = 'XLL',
    XCP = 'XCP',
    XSO = 'XSO',

    INFO = 'INFO', // special value for sub-menu
}

export enum BusinessState {
    ACTIVE = 'Active',
    DRAFT = 'Draft'
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
    AuthLearnMore = 'auth-options-learn-more',
    PaymentTypeAccountCreation = 'payment-type-in-account-creation',
    LinkToNewNameRequestApp ='link-to-new-name-request-app',
    EnableMandatoryAddress = 'enable-mandatory-address',
    EnableGovmInvite = 'enable-govm-account-invite',
    HideProductPackage = 'hide-product-packages',
    EnableOrgNameAutoComplete = 'enable-org-name-auto-complete',
    IaSupportedEntities = 'ia-supported-entities',
    EnableFasDashboard = 'enable-fas-dashboard',
    DisableGovNAccountCreation='disable-govn-account',
    EnableSpGpDba='enable-sp-gp-dba',
    ProductBusSearchStatus='product-BUSINESS_SEARCH-status',
    ProductBusSearchPremTooltip='product-BUSINESS_SEARCH-prem-tooltip',
    ProductCSOStatus='product-CSO-status',
    ProductWillsStatus='product-VS-status',
    ProductSiteRegistryStatus='product-ESRA-status',
    ProductBCAStatus='product-BCA-status'
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
    CREDIT_CARD = 'CC',
    BCOL = 'DRAWDOWN',
    DIRECT_PAY = 'DIRECT_PAY',
    ONLINE_BANKING = 'ONLINE_BANKING',
    PAD = 'PAD',
    EJV = 'EJV'
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

export enum productStatus {
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
    BCEID_ADMIN_REVIEW = 'BCeID Admin'
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
export const ALLOWED_URIS_FOR_PENDING_ORGS: string[] = ['setup-non-bcsc-account']

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
