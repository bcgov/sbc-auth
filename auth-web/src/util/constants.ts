
export enum SessionStorageKeys {
    KeyCloakToken = 'KEYCLOAK_TOKEN',
    KeyCloakRefreshToken = 'KEYCLOAK_REFRESH_TOKEN',
    KeyCloakIdToken = 'KEYCLOAK_ID_TOKEN',
    ApiConfigKey = 'AUTH_API_CONFIG',
    BusinessIdentifierKey = 'BUSINESS_IDENTIFIER',
    UserFullName = 'USER_FULL_NAME',
    UserKcId = 'USER_KC_ID',
    PreventStorageSync = 'PREVENT_STORAGE_SYNC',
    AccountName = 'ACCOUNT_NAME',
    UserAccountType = 'USER_ACCOUNT_TYPE',
    PendingApprovalCount = 'PENDING_APPROVAL_COUNT',
    CurrentAccount = 'CURRENT_ACCOUNT',
    NamesRequestNumberKey = 'NR_NUMBER',
    LaunchDarklyFlags = 'LD_FLAGS'
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
    CREATE_EXTRAPROV_ACCOUNT = 'setup-extra-prov-account',
    DUPLICATE_TEAM_MESAGE = 'duplicateteam',
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
    SETUP_ACCOUNT_OUT_OF_PROVINCE = 'extraprov-info',
    SETUP_ACCOUNT_OUT_OF_PROVINCE_INSTRUCTIONS = 'instructions',
    SETUP_ACCOUNT_OUT_OF_PROVINCE_DOWNLOAD = 'download',
    EDIT_ACCOUNT_TYPE= '/change-account',
    STAFF_DASHBOARD= 'searchbusiness',
    STAFF_SETUP_ACCOUNT = 'staff-setup-account'
}

export enum Account {
    // ANONYMOUS = 'ANONYMOUS',
    PREMIUM = 'PREMIUM',
    BASIC = 'BASIC',
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
    ANONYMOUS = 'ANONYMOUS'
}

export enum AccountStatus {
    ACTIVE = 'ACTIVE',
    REJECTED = 'REJECTED',
    PENDING_AFFIDAVIT_REVIEW = 'PENDING_AFFIDAVIT_REVIEW'
}
