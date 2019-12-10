
export enum SessionStorageKeys {
    KeyCloakToken = 'KEYCLOAK_TOKEN',
    KeyCloakRefreshToken = 'KEYCLOAK_REFRESH_TOKEN',
    Idtoken = 'KEYCLOAK_ID_TOKEN',
    ApiConfigKey = 'AUTH_API_CONFIG',
    BusinessIdentifierKey = 'BUSINESS_IDENTIFIER',
    UserFullName = 'USER_FULL_NAME'
}

export enum Role {
    Staff = 'staff',
    Public = 'public_user',
    Edit = 'edit',
    Basic = 'basic'
}

export enum Pages {
    USER_PROFILE = 'userprofile',
    CREATE_TEAM = 'createteam',
    DUPLICATE_TEAM_MESAGE = 'duplicateteam',
    PENDING_APPROVAL = 'pendingapproval',
    MAIN = 'main'
}
