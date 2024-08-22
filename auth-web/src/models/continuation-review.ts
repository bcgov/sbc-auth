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
  futureEffectiveDate: string // 'YYYY-MM-DDTHH:MM.SS.000+00:00
  nrExpiryDate: string // 'YYYY-MM-DDTHH:MM.SS.000+00:00
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

/** The Continuation Review search and sort params. */
export interface ReviewFilterParams {
    startDate?: string // The start date for submission date range
    endDate?: string // The end date for submission date range
    startEffectiveDate?: string // The start date for future effective date range
    endEffectiveDate?: string // The end date for future effective date range
    page?: number
    limit?: number
    nrNumber?: string
    identifier?: string
    completingParty?: string
    decisionMadeBy?: string
    status?: string[]
    sortBy?: string
    sortDesc?: boolean
  }

/** The Continuation Review API returns search results. */
export interface ReviewList {
    reviews: ContinuationReviewIF[]
    limit: number
    page: number
    total: number
  }
