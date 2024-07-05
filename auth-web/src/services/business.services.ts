import { BNRequest, ResubmitBNRequest } from '@/models/request-tracker'
import { Business, BusinessRequest, FolioNumberload, PasscodeResetLoad } from '@/models/business'
import { AxiosResponse } from 'axios'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import { ContinuationReviewIF } from '@/models/continuation-review'
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
   * Fetches a continuation review object.
   * @param reviewId the review id
   * @returns a promise to return the axios response or the error response
   */
  static async fetchContinuationReview (reviewId: number): Promise<ContinuationReviewIF> {
    // safety check
    if (!reviewId) {
      throw new Error('Invalid parameters')
    }

    // *** TODO: once the API is ready, replace this mocked data with the Axios call below
    return new Promise(resolve => resolve({
      review: {},
      results: [],
      filing: {
        continuationIn: {
          authorization: {
            date: '2024-07-01',
            files: [
              {
                fileKey: '0071dbd6-6095-46f6-b5e4-cc859b0ebf27.pdf',
                fileName: 'My Authorization Document.pdf'
              },
              {
                fileKey: 'xxx.pdf',
                fileName: 'Invalid File.pdf'
              }
            ]
          },
          business: {
            foundingDate: '2001-05-03T07:00:00.000+00:00',
            identifier: 'A0054444',
            legalName: 'FIRST AWIQ SHOPPING CENTRES BC LIMITED'
          },
          foreignJurisdiction: {
            affidavitFileKey: '007bd7bd-d421-49a9-9925-03ce561d044f.pdf',
            affidavitFileName: 'My Director Affidavit.pdf',
            country: 'CA',
            identifier: 'AB-5444',
            incorporationDate: '2001-04-02',
            legalName: 'FIRST AWIQ SHOPPING CENTRES ALBERTA UNLIMITED',
            region: 'AB',
            taxId: '123456789'
          },
          mode: 'EXPRO',
          nameRequest: {
            legalType: 'CUL'
          }
        }
      }
    }))

    // const url = `${ConfigHelper.getLegalAPIV2Url()}/continuation-reviews/${reviewId}`
    // return axios.get(url)
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
    if (!documentKey || !documentName) {
      throw new Error('Invalid parameters')
    }

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
}
