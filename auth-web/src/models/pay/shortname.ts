import { DataOptions } from 'vuetify'
import { ShortNameStatus } from '@/util/constants'

export interface LinkedShortnameFilterParams {
  isActive: boolean
  pageNumber: number
  pageLimit: number
  filterPayload: {
    accountName?: string
    shortName?: string
    accountBranch?: string
    accountId?: string
    state: ShortNameStatus
  }
}

export interface LinkedShortnameState {
  results: any[]
  totalResults: number
  loading: boolean
  filters: LinkedShortnameFilterParams
  actionDropdown: any[]
  options: DataOptions
}

export interface UnLinkedShortnameFilterParams {
  isActive: boolean
  pageNumber: number
  pageLimit: number
  filterPayload: {
    accountName?: string
    shortName?: string
    accountBranch?: string
    accountId?: string
    state: ShortNameStatus
  }
}
