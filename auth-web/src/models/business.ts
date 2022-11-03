import { CorpTypes, FilingTypes, LearFilingTypes, NrTargetTypes } from '@/util/constants'
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
    code: string // may be corp type or TMP / NR / RTMP
    default?: boolean
    desc: string
    legalType: CorpTypes // actual corp type
}

export interface Business {
    businessIdentifier: string
    businessNumber?: string
    name?: string
    contacts?: Contact[]
    corpType: CorpType,
    folioNumber: string,
    lastModified?: string,
    modified?: string
    modifiedBy?: string
    nameRequest?: NameRequest
    nrNumber?: string
    status?: string
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
    actions?: Array<Actions>
    consentFlag?: string
    names?: Array<Names>
    id?: number
    legalType: CorpTypes
    nrNumber?: string
    state?: string
    applicantEmail?: string
    applicantPhone?: string
    enableIncorporation?: boolean
    folioNumber?: string
    target?: NrTargetTypes
    entityTypeCd?: string
    natureOfBusiness?: string
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

// Actions interface to match external data provided from lear.
export interface Actions {
    URL: string,
    entitiesFilingName: string,
    filingName: LearFilingTypes,
}

export interface BusinessRequest {
    filing: {
        header: {
            name: FilingTypes
            accountId: number
        },
        // business is only used in incorporationApplication filing
        business?: {
            legalType: CorpTypes
        },
        incorporationApplication?: {
            nameRequest: NameRequest
        },
        registration?: {
            nameRequest: NameRequest
            businessType?: string // SP or DBA
            business: {
                natureOfBusiness?: string
            }
        }
    }
}

export interface PasscodeResetLoad {
    businessIdentifier: string,
    passcodeResetEmail: string,
    resetPasscode: boolean
}

export interface LearBusiness {
    identifier: string,
    legalName: string,
    taxId?: string
}
