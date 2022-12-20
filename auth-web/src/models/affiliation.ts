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
