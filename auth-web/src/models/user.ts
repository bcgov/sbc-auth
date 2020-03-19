import { Contact } from '@/models/contact'

export interface User {
    firstname: string;
    lastname: string;
    username: string;
    modified?: Date
    userTerms?: UserTerms
}

export interface UserTerms {
    isTermsOfUseAccepted: boolean
    termsOfUseAcceptedVersion: string
}

export interface UserProfileRequestBody {
    username: string
    password: string
}
