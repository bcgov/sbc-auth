export interface StatementListItem {
  endDate: string
  frequency: string
  id: number,
  startDate: string
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
