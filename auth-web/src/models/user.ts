import { Contact } from '@/models/contact'
import { RoleInfo } from '@/models/Organization'
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
