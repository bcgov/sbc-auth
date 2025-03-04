import { BNRequest, ResubmitBNRequest } from '@/models/request-tracker'
import { Business, BusinessRequest, FolioNumberload, PasscodeResetLoad } from '@/models/business'
import { ContinuationReviewIF, ReviewFilterParams, ReviewStatus } from '@/models/continuation-review'
import { AxiosResponse } from 'axios'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import { axios } from '@/util/http-util'

export default class BusinessService {
  static async getBusiness (businessIdentifier: string): Promise<AxiosResponse<Business>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/entities/${businessIdentifier}`)
  }

  static async createBusiness (business: Business): Promise<AxiosResponse<Business>> {
    return axios.post(`${ConfigHelper.getAuthAPIUrl()}/entities`, business)
  }

  static async getAuthentication (businessIdentifier: string): Promise<AxiosResponse<any>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/entities/${businessIdentifier}/authentication`)
  }

  static async getMaskedContacts (businessIdentifier: string): Promise<AxiosResponse<Contact>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/entities/${businessIdentifier}/contacts`)
  }

  static async addContact (business: Business, contact: Contact): Promise<AxiosResponse<Business>> {
    return axios.post(`${ConfigHelper.getAuthAPIUrl()}/entities/${business.businessIdentifier}/contacts`, contact)
  }

  static async updateContact (business: Business, contact: Contact): Promise<AxiosResponse<Business>> {
    return axios.put(`${ConfigHelper.getAuthAPIUrl()}/entities/${business.businessIdentifier}/contacts`, contact)
  }

  static async searchBusiness (businessIdentifier: string): Promise<AxiosResponse<any>> {
    return axios.get(`${ConfigHelper.getLegalAPIV2Url()}/businesses/${businessIdentifier}`)
  }

  static async createDraftFiling (filingBody: BusinessRequest): Promise<AxiosResponse<any>> {
    return axios.post(`${ConfigHelper.getLegalAPIV2Url()}/businesses?draft=true`, filingBody)
  }

  static async deleteBusinessFiling (businessRegNumber: string, filingId: string): Promise<AxiosResponse<any>> {
    return axios.delete(`${ConfigHelper.getLegalAPIV2Url()}/businesses/${businessRegNumber}/filings/${filingId}`)
  }

  static async getFilings (businessRegNumber: string): Promise<AxiosResponse<any>> {
    return axios.get(`${ConfigHelper.getLegalAPIV2Url()}/businesses/${businessRegNumber}/filings`)
  }

  static async searchFiling (filingID: string): Promise<AxiosResponse<any>> {
    return axios.get(`${ConfigHelper.getLegalAPIV2Url()}/businesses/filings/search/${filingID}`)
  }

  static async updateFolioNumber (folioNumber: FolioNumberload): Promise<AxiosResponse<any>> {
    return axios.patch(`${ConfigHelper.getAuthAPIUrl()}/entities/${folioNumber.businessIdentifier}`, folioNumber)
  }

  static async resetBusinessPasscode (passcodeResetLoad: PasscodeResetLoad): Promise<AxiosResponse<any>> {
    return axios.patch(`${ConfigHelper.getAuthAPIUrl()}/entities/${passcodeResetLoad.businessIdentifier}`,
      {
        businessIdentifier: passcodeResetLoad.businessIdentifier,
        passcodeResetEmail: passcodeResetLoad.passcodeResetEmail,
        resetPasscode: passcodeResetLoad.resetPasscode
      })
  }

  static async createBNRequest (request: BNRequest): Promise<AxiosResponse<any>> {
    let url = `${ConfigHelper.getLegalAPIV2Url()}/admin/bn/${request.businessIdentifier}`
    if (request.businessNumber) {
      url = `${url}/${request.businessNumber}`
    }
    return axios.post(url)
  }

  static async getBNRequests (businessIdentifier: string): Promise<AxiosResponse<any>> {
    const url = `${ConfigHelper.getLegalAPIV2Url()}/requestTracker/bn/${businessIdentifier}`
    return axios.get(url)
  }

  static async resubmitBNRequest (resubmitRequest: ResubmitBNRequest): Promise<AxiosResponse<any>> {
    const url = `${ConfigHelper.getLegalAPIV2Url()}/requestTracker/bn/${resubmitRequest.businessIdentifier}`
    return axios.post(url, resubmitRequest)
  }

  static async getRequestTracker (requestTrackerId: number): Promise<AxiosResponse<any>> {
    const url = `${ConfigHelper.getLegalAPIV2Url()}/requestTracker/${requestTrackerId}`
    return axios.get(url)
  }

  static async fetchBusinessSummary (businessIdentifier: string): Promise<void> {
    const config = {
      headers: { 'Accept': 'application/pdf' },
      responseType: 'blob' as 'json'
    }

    const data = await axios.get(
      `${ConfigHelper.getLegalAPIV2Url()}/businesses/${businessIdentifier}/documents/summary`, config)
    CommonUtils.fileDownload(data?.data, `${businessIdentifier} Summary.pdf`, data?.headers['content-type'])
  }

  /**
   * Fetches a filing by its URL.
   * @param url the full URL of the filing
   * @returns a promise to return the filing
   */
  static async fetchFiling (url: string): Promise<any> {
    // safety check
    if (!url) throw new Error('Invalid parameters')

    return axios.get(url)
      .then(response => {
        const filing = response?.data?.filing
        if (!filing) {
          // eslint-disable-next-line no-console
          console.log('fetchFiling() error - invalid response =', response)
          throw new Error('Invalid API response')
        }
        return filing
      })
  }

  /**
   * Fetches a continuation review object.
   * @param reviewId the review id
   * @returns a promise to return the data or the axios error response
   */
  static async fetchContinuationReview (reviewId: number): Promise<ContinuationReviewIF> {
    // safety check
    if (!reviewId) throw new Error('Invalid parameters')

    const url = `${ConfigHelper.getLegalAPIV2Url()}/admin/reviews/${reviewId}`
    return axios.get(url)
      .then(response => {
        const review = response?.data
        if (!review) {
          // eslint-disable-next-line no-console
          console.log('fetchContinuationReview() error - invalid response =', response)
          throw new Error('Invalid API response')
        }
        return review
      })
  }

  /**
   * Submits a continuation review result.
   * @param status the review status
   * @param comment the optional review comment
   * @returns a promise to return the data or the axios error response
   */
  static async submitContinuationReviewResult (reviewId: number, status: ReviewStatus, comment: string): Promise<any> {
    // safety check
    if (!status) throw new Error('Invalid parameters')

    const data = { status, comment }
    const url = `${ConfigHelper.getLegalAPIV2Url()}/admin/reviews/${reviewId}`

    return axios.post(url, data)
  }

  /**
   * Downloads a Minio document from Legal API and prompts browser to open/save it.
   * @param documentKey the document key
   * @param documentName the document filename
   * @returns a promise to return the axios response or the error response
   * @see CommonUtils.fileDownload() for a similar method
   */
  static async downloadDocument (documentKey: string, documentName: string): Promise<AxiosResponse> {
    // safety checks
    if (!documentKey || !documentName) throw new Error('Invalid parameters')

    const url = `${ConfigHelper.getLegalAPIV2Url()}/documents/${documentKey}`
    const config = {
      headers: { 'Accept': 'application/pdf' },
      responseType: 'blob' as 'json'
    }

    return axios.get(url, config).then(response => {
      if (!response) throw new Error('Null response')

      /* solution below is from https://github.com/axios/axios/issues/1392 */

      // it is necessary to create a new blob object with mime-type explicitly set
      // otherwise only Chrome works like it should
      const blob = new Blob([response.data], { type: 'application/pdf' })

      // use Navigator.msSaveOrOpenBlob if available (possibly IE)
      // warning: this is now deprecated
      // ref: https://developer.mozilla.org/en-US/docs/Web/API/Navigator/msSaveOrOpenBlob
      if (window.navigator && window.navigator['msSaveOrOpenBlob']) {
        window.navigator['msSaveOrOpenBlob'](blob, documentName)
      } else {
        // for other browsers, create a link pointing to the ObjectURL containing the blob
        const url = window.URL.createObjectURL(blob)
        const a = window.document.createElement('a')
        window.document.body.appendChild(a)
        a.setAttribute('style', 'display: none')
        a.href = url
        a.download = documentName
        a.click()
        window.URL.revokeObjectURL(url)
        a.remove()
      }

      return response
    })
  }

  static async searchReviews (reviewFilter: ReviewFilterParams) {
    const params = new URLSearchParams()
    for (const key in reviewFilter) {
      const value = reviewFilter[key]
      if (Array.isArray(value)) {
        // for status, which is an array
        value.forEach(item => params.append(key, item))
      } else {
        params.append(key, value)
      }
    }
    try {
      const response = await axios.get(`${ConfigHelper.getLegalAPIV2Url()}/admin/reviews`, { params })
      if (response?.data) {
        return response.data
      }
      return null
    } catch (error) {
      console.error('Error fetching reviews:', error)
      return null
    }
  }
}
