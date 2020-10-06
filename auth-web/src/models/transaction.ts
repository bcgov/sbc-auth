export interface Transaction {
  createdName: string
  createdOn: string
  id: number,
  paymentMethod: string
  statusCode: string
  updatedName: string
  updatedOn: string
  businessIdentifier: string
  folioNumber: string
  lineItems: LineItem[]
  paid: number
  refund: number
  total: number
  transactionFees: number
}

export interface LineItem {
  description: string
  filingFees: number
  filingTypeCode: string
  futureEffectiveFees: number
  gst: number
  priorityFees: number
  pst: number
  quantity: number
  total: number
  waivedBy: string
  waivedFees: number
}

export interface TransactionFilter {
  dateFilter: {
    startDate: string
    endDate: string
  },
  folioNumber?: string,
  createdBy?: string,
}

export interface TransactionFilterParams {
  filterPayload: TransactionFilter
  pageNumber?: number
  pageLimit?: number
}

export interface TransactionListResponse {
  items: Transaction[]
  limit: number
  page: number
  total: number
}

export interface TransactionTableList {
  transactionsList: TransactionTableRow[]
  limit: number
  page: number
  total: number
}

export interface TransactionTableRow {
  id: number
  transactionNames: string[]
  folioNumber: string
  initiatedBy: string
  transactionDate: string
  totalAmount: number
  status: string
}
