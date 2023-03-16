import { Business, CorpType, NameRequest } from '@/models/business'
import { Contact } from './contact'
import { Organization } from '@/models/Organization'

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

export interface AffiliationFilter {
  businessName?: string,
  businessNumber?: string,
  type?: string,
  status?: string,
  Actions?: string
}

export interface AffiliationResponse {
  identifier: string
  businessNumber?: string
  name?: string
  contacts?: Contact[]
  corpType?: CorpType
  corpSubType?: CorpType
  folioNumber?: string
  lastModified?: string
  modified?: string
  modifiedBy?: string
  nameRequest?: NameRequest
  nrNumber?: string
  status?: string
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
