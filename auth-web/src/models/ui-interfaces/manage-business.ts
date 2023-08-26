import { Business } from '@/models/business'
import { AffiliationInviteInfo } from '@/models/affiliation'

export interface ErrorDetails {
  errorName: string

  errorSource?: object
  errorCode?: number
  errorSummary?: string
  errorDescription?: string
}

export interface EventDetails {
  eventName: string

  entity?: Business
  affiliationInvitation?: AffiliationInviteInfo
}

export interface MainActionButtonClickedEvent {
  name: string
  isError: boolean
  businessIdentifier: string

  details?: ErrorDetails|EventDetails
}
