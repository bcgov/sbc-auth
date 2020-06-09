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

export interface CorpType {
    code: string
    desc: string
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

export interface UpdateBusinessNamePayload {
    businessIdentifier: string
    name: string
}

// see https://github.com/bcgov/business-schemas/blob/master/src/registry_schemas/schemas/name_request.json
export interface NameRequest {
    legalType: string,
    nrNumber?: string
}

export interface BusinessRequest {
    filing: {
        header: {
            name: string,
            accountId: number
        },
        business: {
            legalType: string
        },
        incorporationApplication: {
            nameRequest: NameRequest
        }
    }
}
