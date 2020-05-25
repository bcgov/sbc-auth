import { Contact } from './contact'

export interface LoginPayload {
    businessIdentifier: string
    passCode?: string
    phone?: string
    email?: string
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
    corpType: CorpType,
    folioNumber: string
}

export interface Businesses {
    entities: Business[]
}

export interface CorpType {
    code: string
    desc: string
}

export interface UpdateFilingBody {
    filing: {
        header: {
            name: string,
            accountId: number
        },
        incorporationApplication: {
            nameRequest: {
                nrNumber: string
            }
        }
    }
}
