import { Address } from '@/models/address'

// Interface describing response from MHR api for Qualified Supplier applicant info
export interface QualifiedSupplierApplicant {
  address: Address
  authorizationName: string
  businessName: string
  partyType: string
  phoneExtension: string
  phoneNumber: string
  termsAccepted: boolean
}

// Interface describing Qs Requirements configurations for Staff Task Review
export interface QualifiedSupplierRequirementsConfig {
  boldText?: string
  regularText?: string
}
