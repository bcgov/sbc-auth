export interface EFTAccountsFilterParams {
  isActive: boolean
  pageNumber: number
  pageLimit: number
  filterPayload: {
    accountIdList?: string
  }
}
