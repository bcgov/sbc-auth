import { Contact } from './contact'

export interface LoginPayload {
    businessIdentifier: string
    passCode: string
}

export interface Business {
    businessIdentifier: string
    businessNumber?: string
    name?: string
    contacts?: Contact[]
    corpType: string
}

export interface Businesses {
    entities: Business[]
}
