import { CorpTypes, FilingTypes, LearFilingTypes, NrTargetTypes } from '@/util/constants'
import { NrRequestActionCodes, NrRequestTypeCodes } from '@bcrs-shared-components/enums'
import { AffiliationInviteInfo } from '@/models/affiliation'
import { Contact } from './contact'

export interface LoginPayload {
    businessIdentifier: string
    passCode?: string
    phone?: string
    email?: string
    certifiedByName?: string
}

export interface FolioNumberload {
    businessIdentifier: string
    folioNumber: string
}

export interface CorpType {
    code: CorpTypes // may be actual corp type or overloaded value
    default?: boolean
    desc?: string
}

export interface Business {
    businessIdentifier: string
    businessNumber?: string
    name?: string
    contacts?: Contact[]
    corpType: CorpType
    corpSubType?: CorpType
    folioNumber?: string
    lastModified?: string
    modified?: string
    modifiedBy?: string
    nameRequest?: NameRequest
    nrNumber?: string
    status?: string
    goodStanding?: boolean
    adminFreeze?: boolean
    dissolved?: boolean
    affiliationInvites?: AffiliationInviteInfo[]
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
    actions?: Array<Action>
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
    requestTypeCd?: NrRequestTypeCodes
    requestActionCd?: NrRequestActionCodes
    natureOfBusiness?: string
    expirationDate?: Date
    nrNum?: string
    requestActionCd?: string
    stateCd?: string
    natureBusinessInfo?: string
    applicants?: Array<Applicant>
    corpNum?: string
}

export interface Applicant {
    emailAddress?: string
    phoneNumber?: string
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
export interface Action {
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
