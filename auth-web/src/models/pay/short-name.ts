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
    accountIdList?: string
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
  highlightIndex: number
  snackbar: boolean
  snackbarText: string
  clearFiltersTrigger: number
}

export interface UnlinkedShortNameFilterParams {
  isActive: boolean
  pageNumber: number
  pageLimit: number
  filterPayload: {
    shortName?: string
    transactionDate?: string
    depositAmount?: string
    state: ShortNameStatus
    transactionStartDate?: string
    transactionEndDate?: string
  }
}

export interface UnlinkedShortNameResults {
  shortName?: string
  transactionDate?: string
  depositAmount?: number
  id: number
}

export interface UnlinkedShortNameState {
  results: UnlinkedShortNameResults[]
  totalResults: number
  loading: boolean
  filters: UnlinkedShortNameFilterParams
  actionDropdown: any[]
  options: DataOptions
  shortNameLookupKey: number
  dateRangeReset: number
  clearFiltersTrigger: number
  selectedShortName: object
  showDatePicker: boolean
  dateRangeSelected: boolean
  dateRangeText: string
  accountLinkingErrorDialogTitle: string
  accountLinkingErrorDialogText: string
  isShortNameLinkingDialogOpen: boolean
}
