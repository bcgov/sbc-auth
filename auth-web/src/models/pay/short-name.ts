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

export interface LinkedShortNameResults {
  accountName?: string
  shortName?: string
  accountBranch?: string
  accountId?: string
  id: number
}

export interface LinkedShortNameState {
  results: LinkedShortNameResults[]
  totalResults: number
  loading: boolean
  filters: LinkedShortNameFilterParams
  actionDropdown: any[]
  options: DataOptions
}

export interface UnLinkedShortNameFilterParams {
  isActive: boolean
  pageNumber: number
  pageLimit: number
  filterPayload: {
    shortName?: string
    depositDate?: string
    depositAmount?: number
    state: ShortNameStatus
  }
}

export interface UnLinkedShortNameResults {
  shortName?: string
  depositDate?: string
  depositAmount?: number
  id: number
}

export interface UnLinkedShortNameState {
  results: UnLinkedShortNameResults[]
  totalResults: number
  loading: boolean
  filters: UnLinkedShortNameFilterParams
  actionDropdown: any[]
  options: DataOptions
}
