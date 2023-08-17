import { Contact } from '@/models/contact'

export interface User {
    firstname: string;
    lastname: string;
    username?: string;
    modified?: Date
    userTerms?: UserTerms
    contacts?: Contact[]
    email?: string,
    loginSource?: string
    id?: number
    keycloakGuid?: string
    verified?:boolean
}

export interface UserTerms {
    isTermsOfUseAccepted: boolean
    termsOfUseAcceptedVersion: string
}

export interface UserProfileRequestBody {
    username: string
    password: string
}

export interface DocumentUpload {
    preSignedUrl: string
    key: string
}

export interface UserProfileData {
    firstname: string;
    lastname: string;
    email: string;
    phone: string;
    phoneExtension?: string;
}

export interface UserSettings {
    id: string
    label: string
    type: string
    urlpath: string
    urlorigin: string
    accountType: string // will be only present for accounts
    accountStatus: string
}
