export interface Refund {
  reason: string,
  refundRevenue: refundRevenueType[]
}

export interface refundRevenueType {
  paymentLineItemId: string,
  refundAmount: number,
  refundType: string
}
