export interface RefundRequest {
  reason: string
  refundRevenue?: RefundRevenueType[]
}

export interface RefundRevenueType {
  paymentLineItemId: string
  refundAmount: number
  refundType: string
}
