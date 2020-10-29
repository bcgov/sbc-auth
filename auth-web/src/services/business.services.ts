import { Business, BusinessRequest, FolioNumberload, UpdateBusinessNamePayload } from '@/models/business'
import { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import { axios } from '@/util/http-util.ts'

export default class BusinessService {
  static async getBusiness (businessIdentifier: string): Promise<AxiosResponse<Business>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/entities/${businessIdentifier}`)
  }

  static async createBusiness (business: Business): Promise<AxiosResponse<Business>> {
    return axios.post(`${ConfigHelper.getAuthAPIUrl()}/entities`, business)
  }

  static async addContact (business: Business, contact: Contact): Promise<AxiosResponse<Business>> {
    return axios.post(`${ConfigHelper.getAuthAPIUrl()}/entities/${business.businessIdentifier}/contacts`, contact)
  }

  static async updateContact (business: Business, contact: Contact): Promise<AxiosResponse<Business>> {
    return axios.put(`${ConfigHelper.getAuthAPIUrl()}/entities/${business.businessIdentifier}/contacts`, contact)
  }

  static async searchBusiness (businessIdentifier: string): Promise<AxiosResponse<any>> {
    return axios.get(`${ConfigHelper.getLegalAPIUrl()}/businesses/${businessIdentifier}`)
  }

  static async createNamedBusiness (filingBody: BusinessRequest): Promise<AxiosResponse<any>> {
    return axios.post(`${ConfigHelper.getLegalAPIUrl()}/businesses?draft=true`, filingBody)
  }

  static async createNumberedBusiness (filingBody: BusinessRequest): Promise<AxiosResponse<any>> {
    return axios.post(`${ConfigHelper.getLegalAPIUrl()}/businesses?draft=true`, filingBody)
  }
  static async deleteBusinessFiling (businessRegNumber: string, filingId: string): Promise<AxiosResponse<any>> {
    return axios.delete(`${ConfigHelper.getLegalAPIUrl()}/businesses/${businessRegNumber}/filings/${filingId}`)
  }
  static async getFilings (businessRegNumber: string): Promise<AxiosResponse<any>> {
    return axios.get(`${ConfigHelper.getLegalAPIUrl()}/businesses/${businessRegNumber}/filings`)
  }

  static async updateFolioNumber (folioNumber: FolioNumberload): Promise<AxiosResponse<any>> {
    return axios.patch(`${ConfigHelper.getAuthAPIUrl()}/entities/${folioNumber.businessIdentifier}`, folioNumber)
  }

  static async updateBusinessName (updatePayload: UpdateBusinessNamePayload): Promise<AxiosResponse<any>> {
    return axios.patch(`${ConfigHelper.getAuthAPIUrl()}/entities/${updatePayload.businessIdentifier}`, updatePayload)
  }
}
