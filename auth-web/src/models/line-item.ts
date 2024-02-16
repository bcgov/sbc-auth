export interface LineItem {
  description: string
  filingFees: number
  futureEffectiveFees: number
  gst: number
  id?: number
  priorityFees: number
  pst: number
  quantity: number
  serviceFees: number
  statusCode?: string
  total: number
  waivedBy: string
  waivedFees: number
}
