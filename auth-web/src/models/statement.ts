export interface StatementListItem {
  createdOn?: string
  frequency: string
  fromDate?: string
  id?: number
  isOverdue?: boolean
  isNew?: boolean
  toDate?: string
  paymentMethods?: string[]
}

export interface Statement {
  id?: number
  isInterimStatement?: boolean
  frequency: string
  fromDate: string
  toDate: string
  paymentMethods: string[]
}

export interface StatementSettings {
  currentFrequency?: StatementListItem
  frequencies: Frequencies[]
}

export interface StatementsSummary {
  oldestDueDate?: string
  totalDue: number
  totalInvoiceDue: number
}

export interface Frequencies {
  frequency: string
  startDate: string
}

export interface StatementFilterParams {
  pageNumber?: number
  pageLimit?: number
  filterPayload: {
    isOwing?: string
  }
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
