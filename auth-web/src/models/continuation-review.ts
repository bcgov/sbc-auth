export enum ReviewStatus {
  AWAITING_REVIEW = 'AWAITING_REVIEW',
  CHANGE_REQUESTED = 'CHANGE_REQUESTED',
  RESUBMITTED = 'RESUBMITTED',
  REJECTED = 'REJECTED',
  ABANDONED = 'ABANDONED',
  APPROVED = 'APPROVED'
}

/** The Result object inside the Continuation Review API response. */
export interface ContinuationReviewResultIF {
  comments: string // max 2000 chars
  creationDate: string // 'YYYY-MM-DDTHH:MM.SS.000+00:00'
  reviewer: string
  status: ReviewStatus
  submissionDate: string // 'YYYY-MM-DDTHH:MM.SS.000+00:00'
}

/** The Continuation Review API response. */
export interface ContinuationReviewIF {
  completingParty: string
  creationDate: string // 'YYYY-MM-DDTHH:MM.SS.000+00:00'
  filingId: number
  filingLink: string // URL for the continuation in filing
  id: number
  identifier: string // foreign identifying number
  nrNumber: string
  results: Array<ContinuationReviewResultIF>
  status: ReviewStatus
  submissionDate: string // 'YYYY-MM-DDTHH:MM.SS.000+00:00
}

/** The Continuation In object in the filing API response. */
export interface ContinuationFilingIF {
  header: any // we don't care about this
  business: any // we don't care about this
  continuationIn: {
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
    contactPoint: any // we don't care about this
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
    isConfirmed: any // we don't care about this
    mode: 'EXPRO' | 'MANUAL'
    nameRequest: {
      legalType: string
    }
    nameTranslations: any // we don't care about this
    offices: any // we don't care about this
    parties: any // we don't care about this
    shareStructure: any // we don't care about this
    status: any // we don't care about this
  }
}
