import { DataOptions } from 'vuetify'

export interface EFTTransaction {
  id: number
  shortNameId: number
  depositAmount: number
  depositDate: string
  transactionDate: string
  transactionType: string
  eftRefundId: number
}

export interface EFTTransactionFilterParams {
  pageNumber?: number
  pageLimit?: number
}

export interface EFTTransactionListResponse {
  items: EFTTransaction[]
  limit: number
  page: number
  total: number
  remainingCredit: number
}

export interface EFTTransactionState {
  errorDialogTitle?: string,
  errorDialogText?: string,
  confirmDialogTitle?: string
  confirmDialogText?: string
  confirmObject?: object
  filters: EFTTransactionFilterParams
  loading: boolean
  results: EFTTransaction[]
  totalResults: number,
  options: DataOptions
}

export interface EFTShortnameResponse {
  id: number
  shortName: string
  accountBranch?: string
  accountId?: number
  accountName?: string
  createdOn: string
  depositAmount?: number
  depositDate?: string
  linkedBy?: string
  linkedByName?: string
  linkedOn?: string
  transactionDate?: string
  transactionId?: string
}
