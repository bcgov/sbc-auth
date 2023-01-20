import { InvoiceStatus, PaymentTypes } from '@/util/constants'
import { LineItem } from '.'

export interface Transaction {
  businessIdentifier: string
  createdName: string
  createdOn: string
  folioNumber: string
  id: number
  lineItems: LineItem[]
  paid: number
  paymentAccount: {
    accountId: string
    accountName: string
    billable: boolean
  }
  paymentMethod: PaymentTypes
  refund: number
  statusCode: InvoiceStatus
  total: number
  updatedOn: string
}

export interface TransactionFilter {
  createdBy?: string,
  createdName?: string,
  dateFilter: {
    startDate: string
    endDate: string
  },
  folioNumber?: string,
  id?: string,
  paymentMethod?: PaymentTypes,
  statusCode?: InvoiceStatus
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

export interface TransactionState {
  filters: TransactionFilterParams
  loading: boolean
  results: Transaction[]
  totalResults: number
}
