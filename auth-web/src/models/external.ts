import { Address } from '@/models/address'
import { ProductStatus } from '@/util/constants'

// Interface describing response from MHR api for Qualified Supplier applicant info
export interface QualifiedSupplierApplicant {
  address: Address
  authorizationName: string
  businessName: string
  dbaName?: string
  partyType?: string
  phoneExtension?: string
  phoneNumber?: string
  termsAccepted: boolean
  mfLocation?: Address
}

// Interface describing response from MHR api for Qualified Supplier applicant info
export interface MhrManufacturerInfoIF {
  authorizationName?: string
  dbaName?: string
  description: {
    manufacturer: string
  }
  location: {
    address: Address
    dealerName: string
    leaveProvince: boolean
    locationType: string
  }
  ownerGroups: [
    {
      groupId: number
      owners: [
        {
          address: Address
          organizationName: string
          partyType: string
          phoneNumber: string
        }
      ]
      type: string
    }
  ],
  submittingParty: {
    address: Address
    businessName: string
  }
  termsAccepted: boolean
}

// Interface describing Qs Requirements configurations for Staff Task Review
export interface QualifiedSupplierRequirementsConfig {
  boldText?: string
  regularText?: string
}

export interface ProductStatusMsgContentIF {
  status: ProductStatus
  icon: string
  color: string
  msg: string
}
