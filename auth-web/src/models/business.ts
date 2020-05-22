import { Contact } from './contact'

export interface LoginPayload {
    businessIdentifier: string
    passCode: string
}

export interface FolioNumberload {
    businessIdentifier: string
    folioNumber: string
}
export interface Business {
    businessIdentifier: string
    businessNumber?: string
    name?: string
    contacts?: Contact[]
    corpType: string,
    folioNumber: string
}

export interface Businesses {
    entities: Business[]
}

export interface NumberedBusinessRequest {
    filing: {
        header: {
            name: string,
            accountId: number
        }
    }
}
