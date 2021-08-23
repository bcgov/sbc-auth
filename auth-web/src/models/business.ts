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
    folioNumber: string,
    nameRequest?: NameRequest
}

export interface BusinessSearchResultDto {
    businessIdentifier: string
    businessNumber?: string
    name?: string
    accessType?: string
    orgType?: string
    statusCode?:string
    account: string
    entity?: string
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
    names?: Array<Names>
    id?: number,
    legalType: string,
    nrNumber?: string,
    state?: string,
    applicantEmail?: string,
    applicantPhone?: string
}

// Names interface to match external data provided from lear.
export interface Names {
    /* eslint-disable camelcase */
    decision_text: string,
    name_type_cd: string,
    designation: string,
    name: string,
    state: string
    /* eslint-disable camelcase */
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

export interface PasscodeResetLoad {
    businessIdentifier: string,
    passcodeResetEmail: string,
    resetPasscode: boolean
}
