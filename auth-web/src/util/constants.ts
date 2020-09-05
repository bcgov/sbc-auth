
export enum SessionStorageKeys {
    KeyCloakToken = 'KEYCLOAK_TOKEN',
    ApiConfigKey = 'AUTH_API_CONFIG',
    BusinessIdentifierKey = 'BUSINESS_ID',
    CurrentAccount = 'CURRENT_ACCOUNT',
    LaunchDarklyFlags = 'LD_FLAGS',
    ExtraProvincialUser = 'EXTRAPROVINCIAL_USER',
    SessionSynced = 'SESSION_SYNCED',
    InvitationToken = 'INV_TOKEN'
}

export enum Role {
    Staff = 'staff',
    Public = 'public_user',
    Edit = 'edit',
    Basic = 'basic',
    // StaffAdmin = 'create_accounts',
    StaffCreateAccounts = 'create_accounts',
    // StaffAdminBCOL = 'manage_accounts',
    StaffManageAccounts = 'manage_accounts',
    AnonymousUser = 'anonymous_user',
    StaffViewAccounts = 'view_accounts',
    Tester = 'tester',
    AccountHolder = 'account_holder',
    PublicUser = 'public_user',
    AdminStaff = 'admin'
}

export enum Pages {
    USER_PROFILE = 'userprofile',
    CREATE_ACCOUNT = 'setup-account',
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
    EDIT_ACCOUNT_TYPE= '/change-account',
    STAFF_DASHBOARD= '/searchbusiness',
    STAFF_SETUP_ACCOUNT = 'staff-setup-account',
    CONFIRM_TOKEN = 'confirmtoken',
}

export enum Account {
    // ANONYMOUS = 'ANONYMOUS',
    PREMIUM = 'PREMIUM',
    BASIC = 'BASIC',
}

export enum AccountStatus {
    ACTIVE = 'ACTIVE',
    INACTIVE = 'INACTIVE',
    REJECTED = 'REJECTED',
    PENDING_AFFIDAVIT_REVIEW = 'PENDING_AFFIDAVIT_REVIEW',
    PENDING_ACTIVATION = 'PENDING_ACTIVATION'
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

export type Actions = 'upgrade' | 'downgrade'

export enum TransactionStatus {
    COMPLETED = 'Completed',
    PENDING = 'Pending',
    CANCELLED = 'Cancelled'
}

export enum FilingTypes {
    INCORPORATION_APPLICATION = 'incorporationApplication'
}

export enum LegalTypes {
    BCOMP = 'BC',
    COOP = 'CP',
    CORP = 'CR'
}

export enum CorpType {
    COOP = 'CP',
    NEW_BUSINESS = 'TMP',
    BCOMP = 'BC',
    NAME_REQUEST = 'NR'
}

export enum AccessType {
    REGULAR = 'REGULAR',
    EXTRA_PROVINCIAL = 'EXTRA_PROVINCIAL',
    ANONYMOUS = 'ANONYMOUS',
    REGULAR_BCEID = 'REGULAR_BCEID'
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
    VIEW_ADMIN_CONTACT = 'VIEW_ADMIN_CONTACT',
}

export enum LDFlags {
    AuthLearnMore = 'auth-options-learn-more'
}
