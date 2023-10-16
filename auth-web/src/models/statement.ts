export interface StatementListItem {
  createdOn?: string
  frequency: string
  fromDate?: string
  id?: number
  isOverdue?: boolean
  isNew?: boolean
  toDate?: string
}

export interface StatementSettings {
  currentFrequency?: StatementListItem
  frequencies: Frequencies[]
}

export interface StatementsSummary {
  oldestOverdueDate?: string
  totalDue: number
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
  accountName?: string
  statementNotificationEnabled: boolean
  recipients: StatementRecipient[]
}
