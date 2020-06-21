
export enum SessionStorageKeys {
    KeyCloakToken = 'KEYCLOAK_TOKEN',
    ApiConfigKey = 'AUTH_API_CONFIG',
    BusinessIdentifierKey = 'BUSINESS_IDENTIFIER',
    UserKcId = 'USER_KC_ID',
    UserAccountType = 'USER_ACCOUNT_TYPE',
    CurrentAccount = 'CURRENT_ACCOUNT',
    LaunchDarklyFlags = 'LD_FLAGS',
    ExtraProvincialUser = 'EXTRAPROVINCIAL_USER'
}

export enum Role {
    Staff = 'staff',
    Public = 'public_user',
    Edit = 'edit',
    Basic = 'basic',
    StaffAdmin = 'staff_admin',
    StaffAdminBCOL = 'bcol_staff_admin',
    AnonymousUser = 'anonymous_user',
    Tester = 'tester'
}

export enum Pages {
    USER_PROFILE = 'userprofile',
    CREATE_ACCOUNT = 'setup-account',
    CREATE_NON_BCSC_ACCOUNT = 'setup-non-bcsc-account',
    PENDING_APPROVAL = 'pendingapproval',
    PENDING_AFFIDAVIT_APPROVAL = 'pendingaffidavitapproval',
    MAIN = 'account',
    SIGNIN = 'signin',
    SIGNOUT = 'signout',
    CREATE_USER_PROFILE = 'createuserprofile',
    SEARCH_BUSINESS = 'searchbusiness',
    DIRSEARCH_CONFIRM_TOKEN = 'dirsearch-confirmtoken',
    USER_PROFILE_TERMS = 'userprofileterms',
    USER_PROFILE_TERMS_DECLINE = 'unauthorizedtermsdecline',
    HOME = 'home',
    SETUP_ACCOUNT_NON_BCSC = 'nonbcsc-info',
    SETUP_ACCOUNT_NON_BCSC_INSTRUCTIONS = 'instructions',
    SETUP_ACCOUNT_NON_BCSC_DOWNLOAD = 'download',
    EDIT_ACCOUNT_TYPE= '/change-account',
    STAFF_DASHBOARD= 'searchbusiness',
    STAFF_SETUP_ACCOUNT = 'staff-setup-account'
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
    PENDING_AFFIDAVIT_REVIEW = 'PENDING_AFFIDAVIT_REVIEW'
}

export enum IdpHint {
    BCROS = 'bcros',
    IDIR = 'idir',
    BCSC = 'bcsc'
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
