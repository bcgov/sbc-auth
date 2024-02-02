export interface LinkedShortNameFilterParams {
  isActive: false,
  pageNumber: 1,
  pageLimit: 20,
  filterPayload: {
    accountName?: string,
    shortName?: string,
    accountBranch?: string,
    accountId?: string
  }
}
