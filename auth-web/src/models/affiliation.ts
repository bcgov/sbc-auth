import { Action, Applicant, Business, Businesses, CorpType, Names } from '@/models/business'
import { CorpTypes, NrTargetTypes } from '@/util/constants'
import { OrgNameAndId, Organization } from '@/models/Organization'
import { Contact } from './contact'
import { Organization } from '@/models/Organization'
import { NrRequestTypeCodes } from '@bcrs-shared-components/enums'

export interface CreateRequestBody {
  businessIdentifier: string
  certifiedByName: string
  passCode: string
}

export interface CreateNRAffiliationRequestBody {
  businessIdentifier: string
  phone?: string
  email?: string
}

export interface Affiliation {
  organization: Organization
  business: Business
}

export const AffiliationInvitationStatus = {
  Pending: 'PENDING',
  Accepted: 'ACCEPTED',
  Expired: 'EXPIRED',
  Failed: 'FAILED'
}

export interface AffiliationInviteInfo {
  id: number
  type: string
  status: string
  business: Business
  fromOrg: OrgNameAndId
  toOrg: OrgNameAndId
}

export interface AffiliationFilter {
  businessName?: string,
  businessNumber?: string,
  type?: string,
  status?: string,
  actions?: string
}

export interface AffiliationResponse {
  identifier?: string
  draftType?: CorpTypes
  legalType?: CorpTypes
  businessNumber?: string
  name?: string
  legalName?: string
  contacts?: Contact[]
  corpType?: CorpType
  corpSubType?: CorpType
  folioNumber?: string
  lastModified?: string
  modified?: string
  modifiedBy?: string
  nameRequest?: NameRequestResponse
  nrNumber?: string
  state?: string
  goodStanding?: boolean
  adminFreeze?: boolean
  dissolved?: boolean
}

export interface NameRequestResponse {
  actions?: Array<Action>
  consentFlag?: string
  names?: Array<Names>
  id?: number
  legalType: CorpTypes
  state?: string
  applicantEmail?: string
  applicantPhone?: string
  enableIncorporation?: boolean
  folioNumber?: string
  target?: NrTargetTypes
  entityTypeCd?: string
  requestTypeCd?: NrRequestTypeCodes
  natureOfBusiness?: string
  expirationDate?: Date
  nrNum?: string
  stateCd?: string
  natureBusinessInfo?: string
  applicants?: Array<Applicant>
}

export interface AffiliationsResponse {
  entities: AffiliationResponse[]
}

export interface AffiliationFilterParams {
  isActive: boolean
  filterPayload: AffiliationFilter
}

export interface AffiliationState {
  [x: string]: any

  affiliations: any
  filters: {
    isActive: boolean
    filterPayload: AffiliationFilter
  }
  loading: boolean
  results: Business[]
  totalResults: number
}
