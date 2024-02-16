import { RequestTrackerType } from '@/util/constants'

export interface RequestTracker {
  id: number
  requestType: RequestTrackerType
  isProcessed: boolean
  serviceName: string
  isAdmin: boolean
  creationDate: string
  request?: string // Plain XML. Available when requesting by requestTrackerId
  response?: string // Plain XML. Available when requesting by requestTrackerId
}

export interface BNRequest {
  businessIdentifier: string
  businessNumber?: string
}

export interface ResubmitBNRequest {
  businessIdentifier: string
  requestType: RequestTrackerType
  request: string
}
