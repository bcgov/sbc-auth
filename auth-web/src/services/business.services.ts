import { Business } from '@/models/business'
import Axios, { AxiosPromise, AxiosResponse } from 'axios'
import configHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'

interface BusinessService {
  getBusiness: (businessNumber: string) => Promise<AxiosResponse<Business>>
  createBusiness: (business: Business) => Promise<AxiosResponse<Business>>
  addContact: (business: Business, contact: Contact) => Promise<AxiosResponse<Business>>
  updateContact: (business: Business, coontact: Contact) => Promise<AxiosResponse<Business>>
}

export default {
  async getBusiness (businessIdentifier: string): Promise<AxiosResponse<Business>> {
    return Axios.get(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/entities/${businessIdentifier}`)
  },
  async createBusiness (business: Business): Promise<AxiosResponse<Business>> {
    return Axios.post(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/entities`, business)
  },
  async addContact (business: Business, contact: Contact): Promise<AxiosResponse<Business>> {
    return Axios.post(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/entities/${business.businessIdentifier}/contact`, contact)
  },
  async updateContact (business: Business, contact: Contact): Promise<AxiosResponse<Business>> {
    return Axios.put(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/entities/${business.businessIdentifier}/contact`, contact)
  }
} as BusinessService
