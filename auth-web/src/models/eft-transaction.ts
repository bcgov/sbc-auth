export interface EFTTransaction {
  id: number
  shortNameId: number
  depositAmount: number
  depositDate: string
  transactionDate: string
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
  filters: EFTTransactionFilterParams
  loading: boolean
  results: EFTTransaction[]
  totalResults: number
}

export interface EFTShortnameResponse {
  accountBranch: string
  accountId: number
  accountName: string
  createdOn: string
  depositAmount: number
  depositDate: string
  id: number
  linkedBy: string
  linkedByName: string
  linkedOn: string
  shortName: string
  transactionDate: string
  transactionId: string
}
