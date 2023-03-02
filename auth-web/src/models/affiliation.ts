import { Business } from '@/models/business'
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

export interface AffiliationFilterParams {
  isActive: boolean
  filterPayload: AffiliationFilter
  pageNumber?: number
  pageLimit?: number
}

export interface AffiliationState {
  filters: AffiliationFilterParams
  loading: boolean
  results: Business[]
  totalResults: number
}
