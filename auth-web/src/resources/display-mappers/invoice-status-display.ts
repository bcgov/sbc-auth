import { InvoiceStatus } from '@/util/constants'

export const invoiceStatusDisplay = {
  [InvoiceStatus.APPROVED]: 'Processing',
  [InvoiceStatus.CANCELLED]: 'Cancelled',
  [InvoiceStatus.COMPLETED]: 'Completed',
  [InvoiceStatus.CREATED]: 'Created',
  [InvoiceStatus.CREDITED]: 'Credited',
  [InvoiceStatus.DELETED]: 'Deleted',
  [InvoiceStatus.DELETE_ACCEPTED]: 'Deleted',
  [InvoiceStatus.PAID]: 'Completed',
  [InvoiceStatus.PARTIAL]: 'Partial Paid',
  [InvoiceStatus.PENDING]: 'Pending',
  [InvoiceStatus.REFUNDED]: 'Refunded',
  [InvoiceStatus.REFUND_REQUESTED]: 'Refund Requested',
  // not sure about below
  [InvoiceStatus.SETTLEMENT_SCHEDULED]: 'Processing',
  [InvoiceStatus.UPDATE_REVENUE_ACCOUNT]: 'Completed',
  [InvoiceStatus.UPDATE_REVENUE_ACCOUNT_REFUND]: 'Refunded'
}
