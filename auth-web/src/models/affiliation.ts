import { Business } from '@/models/business'
import { Organization } from '@/models/Organization'

export interface CreateRequestBody {
  businessIdentifier: string
  passCode: string
}

export interface Affiliation {
  organization: Organization
  business: Business
}
