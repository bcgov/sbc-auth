import { DataOptions } from 'vuetify'
import { ShortNameStatus } from '@/util/constants'

export interface LinkedShortNameFilterParams {
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

export interface LinkedShortNameState {
  results: any[]
  totalResults: number
  loading: boolean
  filters: LinkedShortNameFilterParams
  actionDropdown: any[]
  options: DataOptions
}

export interface UnlinkedShortNameFilterParams {
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
