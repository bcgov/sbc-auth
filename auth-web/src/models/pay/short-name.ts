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
  clearFiltersTrigger: number
}

export interface ShortNameSummaryFilterParams {
  isActive: boolean
  pageNumber: number
  pageLimit: number
  filterPayload: {
    shortName?: string
    creditsRemaining?: string
    linkedAccountsCount?: string
    paymentReceivedStartDate?: string
    paymentReceivedEndDate?: string
  }
}

export interface ShortNameSummaryResults {
  shortName?: string
  transactionDate?: string
  depositAmount?: number
  id: number
}

export interface ShortNameSummaryState {
  results: ShortNameSummaryResults[]
  totalResults: number
  loading: boolean
  filters: ShortNameSummaryFilterParams
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
  startDate: string
  endDate: string
  snackbarText: string
  snackbar: boolean
  highlightIndex: number
}
