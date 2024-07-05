/** The Review object inside the continuation review API response. */
export interface ContinuationReviewReviewIF {}

/** The Result object inside the continuation review API response. */
export interface ContinuationReviewResultIF {}

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
