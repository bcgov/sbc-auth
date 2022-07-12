export interface RequestTracker {
  id: number
  requestType: string
  isProcessed: boolean
  serviceName: string
  isAdmin: boolean
  request?: string // available when requesting by requestTrackerId
  response?: string // available when requesting by requestTrackerId
}

export interface BNRequest {
  businessIdentifier: string
  businessNumber?: string
}
