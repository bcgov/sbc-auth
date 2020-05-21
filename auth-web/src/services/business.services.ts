import Axios, { AxiosResponse } from 'axios'
import { Business, FolioNumberload, NumberedBusinessRequest } from '@/models/business'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import { addAxiosInterceptors } from 'sbc-common-components/src/util/interceptors'

const axios = addAxiosInterceptors(Axios.create())

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

  static async createNumberedBusiness (numberedBusinessRequest: NumberedBusinessRequest): Promise<AxiosResponse<any>> {
    return axios.post(`${ConfigHelper.getLegalAPIUrl()}/businesses?draft=true`, numberedBusinessRequest)
  }

  static async updateFolioNumber (folioNumber: FolioNumberload): Promise<AxiosResponse<any>> {
    return axios.patch(`${ConfigHelper.getAuthAPIUrl()}/entities/${folioNumber.businessIdentifier}`, folioNumber)
  }
}
