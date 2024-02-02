export interface LinkedShortNameFilterParams {
  isActive: boolean;
  pageNumber: number;
  pageLimit: number;
  filterPayload: {
    accountName?: string,
    shortName?: string,
    accountBranch?: string,
    accountId?: string
  }
}
