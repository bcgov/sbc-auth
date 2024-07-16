export interface RefundRequest {
  reason: string
  refundRevenue?: RefundRevenueType[]
}

export interface RefundRevenueType {
  paymentLineItemId: string
  refundAmount: number
  refundType: string
}

export interface EftRefundRequest {
  shortNameId: number
  refundAmount: number
  casSupplierNum: string
  refundEmail: string
  comment?: string
  shortName?: string
}
