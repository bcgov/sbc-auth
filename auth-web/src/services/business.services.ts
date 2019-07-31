import { Business } from '@/models/business'
import Axios, { AxiosPromise, AxiosResponse } from 'axios'
import configHelper from '@/util/config-helper'

interface BusinessService {
  getBusiness: (businessNumber: string) => Promise<AxiosResponse<Business>>
  createBusiness: (business: Business) => Promise<AxiosResponse<Business>>
  updateBusiness: (business: Business) => Promise<AxiosResponse<Business>>
}

export default {
  async getBusiness (businessIdentifier: string): Promise<AxiosResponse<Business>> {
    return Axios.get(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/entities/${businessIdentifier}`)
  },
  async createBusiness (business: Business): Promise<AxiosResponse<Business>> {
    return Axios.post(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/entities`, business)
  },
  async updateBusiness (business: Business): Promise<AxiosResponse<Business>> {
    return Axios.put(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/entities/${business.businessIdentifier}`, business)
  }
} as BusinessService
