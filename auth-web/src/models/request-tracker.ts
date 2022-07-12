export interface RequestTracker {
  id: number
  requestType: string
  isProcessed: boolean
  serviceName: string
  isAdmin: boolean
  request?: string // Plain XML. Available when requesting by requestTrackerId
  response?: string // Plain XML. Available when requesting by requestTrackerId
}

export interface BNRequest {
  businessIdentifier: string
  businessNumber?: string
}
