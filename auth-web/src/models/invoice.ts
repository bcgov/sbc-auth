export interface InvoiceList {
  consInvNumber?: string
  invoiceNumber: string
  invoices: Invoice[],
  paymentMethod: string
  paymentSystem: string
  statusCode: string
}

export interface Invoice {
  bcolAccount: string
  businessIdentifier: string
  corpTypeCode: string
  createdBy: string
  createdName: string
  createdOn: string
  id: number
  lineItems: LineItem[]
  paid: number
  paymentMethod: string
  refund: number
  serviceFees: number
  statusCode: string
  total: number
}

export interface LineItem {
  description: string
  filingFees: number
  futureEffectiveFees: number
  gst: number
  id: number
  priorityFees: number
  pst: number
  quantity: number
  serviceFees: number
  statusCode: string
  total: number
  waivedBy: string
  waivedFees: number
}

export interface InvoiceListResponse {
  items: InvoiceList[]
  limit: number
  page: number
  total: number
}
