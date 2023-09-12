import { BNRequest, ResubmitBNRequest } from '@/models/request-tracker'
import { Business, BusinessRequest, FolioNumberload, PasscodeResetLoad, UpdateBusinessNamePayload } from '@/models/business'
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

  static async updateFolioNumber (folioNumber: FolioNumberload): Promise<AxiosResponse<any>> {
    return axios.patch(`${ConfigHelper.getAuthAPIUrl()}/entities/${folioNumber.businessIdentifier}`, folioNumber)
  }

  static async updateBusinessName (updatePayload: UpdateBusinessNamePayload): Promise<AxiosResponse<any>> {
    return axios.patch(`${ConfigHelper.getAuthAPIUrl()}/entities/${updatePayload.businessIdentifier}`, updatePayload)
  }

  static async resetBusinessPasscode (passcodeResetLoad: PasscodeResetLoad): Promise<AxiosResponse<any>> {
    return axios.patch(`${ConfigHelper.getAuthAPIUrl()}/entities/${passcodeResetLoad.businessIdentifier}`,
      {
        businessIdentifier: passcodeResetLoad.businessIdentifier,
        passcodeResetEmail: passcodeResetLoad.passcodeResetEmail,
        resetPasscode: passcodeResetLoad.resetPasscode
      })
  }

  static async getNrData (nrNumber: string): Promise<AxiosResponse<any>> {
    return axios.get(`${ConfigHelper.getLegalAPIV2Url()}/nameRequests/${nrNumber}`)
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
}
