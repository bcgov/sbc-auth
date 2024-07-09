export enum ContinuationReviewStatus {
  AWAITING_REVIEW = 'AWAITING_REVIEW',
  CHANGE_REQUESTED = 'CHANGE_REQUESTED',
  RESUBMITTED = 'RESUBMITTED',
  REJECTED = 'REJECTED',
  ACCEPTED = 'ACCEPTED',
  ABANDONED = 'ABANDONED'
}

/** The Review object inside the continuation review API response. */
export interface ContinuationReviewReviewIF {
  id: number
  completingParty: string
  status: ContinuationReviewStatus
  submissionDate: string // 'YYYY-MM-DDTHH:MM.SS.000+00:00
  creationDate: string // 'YYYY-MM-DDTHH:MM.SS.000+00:00'
}

/** The Result object inside the continuation review API response. */
export interface ContinuationReviewResultIF {
  status: ContinuationReviewStatus
  comments: string // max 2000 chars
  reviewer: string
  submissionDate: string // 'YYYY-MM-DDTHH:MM.SS.000+00:00'
  creationDate: string // 'YYYY-MM-DDTHH:MM.SS.000+00:00'
}

/** The Continuation In filing object inside the continuation review API response. */
export interface ContinuationReviewFilingIF {
  authorization: {
    date: string // YYYY-MM-DD
    files: Array<{
      fileKey: string
      fileName: string
    }>
  }
  business: {
    foundingDate: string // YYYY-MM-DDTHH:MM.SS.000+00:00
    identifier: string
    legalName: string
  }
  foreignJurisdiction: {
    affidavitFileKey: string
    affidavitFileName: string
    country: string
    identifier: string
    incorporationDate: string // YYYY-MM-DD
    legalName: string
    region: string
    taxId: string
  }
  mode: 'EXPRO' | 'MANUAL'
  nameRequest: {
    legalType: string
  }
}

/** The Continuation Review API response. */
export interface ContinuationReviewIF {
  review: ContinuationReviewReviewIF
  results: Array<ContinuationReviewResultIF>
  filing: {
    continuationIn: ContinuationReviewFilingIF
  }
}
