export interface StatementListItem {
  createdOn?: string
  frequency: string
  fromDate?: string
  id?: number
  toDate?: string
}

export interface StatementSettings {
  currentFrequency?: StatementListItem
  frequencies: Frequencies[]
}

export interface Frequencies {
  frequency: string
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

export interface StatementRecipient {
  authUserId: number
  email: string
  firstname: string
  lastname: string
  name?: string
}

export interface StatementNotificationSettings {
  authAccountName?: string
  statementNotificationEnabled: boolean
  recipients: StatementRecipient[]
}
