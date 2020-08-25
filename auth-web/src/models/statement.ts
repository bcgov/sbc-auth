export interface StatementListItem {
  createdOn?: string
  frequency: string
  fromDate?: string
  id?: number
  toDate?: string
}

export interface StatementFilterParams {
  pageNumber?: number
  pageLimit?: number
}

export interface StatementListResponse {
  items: StatementListItem[]
  limit: number
  page: number
  total: number
}
