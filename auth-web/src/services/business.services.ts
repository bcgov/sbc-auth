import Axios, { AxiosResponse } from 'axios'
import { CreateRequestBody, Organization } from '@/models/Organization'
import { Affiliation } from '@/models/affiliation'
import { Business } from '@/models/Business'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'

export default class BusinessService {
  static async getBusiness (businessIdentifier: string): Promise<AxiosResponse<Business>> {
    return Axios.get(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/entities/${businessIdentifier}`)
  }

  static async createBusiness (business: Business): Promise<AxiosResponse<Business>> {
    return Axios.post(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/entities`, business)
  }

  static async addContact (business: Business, contact: Contact): Promise<AxiosResponse<Business>> {
    return Axios.post(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/entities/${business.businessIdentifier}/contacts`, contact)
  }

  static async updateContact (business: Business, contact: Contact): Promise<AxiosResponse<Business>> {
    return Axios.put(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/entities/${business.businessIdentifier}/contacts`, contact)
  }

  static async getOrgs (): Promise<AxiosResponse<any>> {
    return Axios.get(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/users/orgs`)
  }

  static async createOrg (org: CreateRequestBody): Promise<AxiosResponse<Organization>> {
    return Axios.post(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs`, org)
  }

  static async createAffiliation (orgIdentifier: number, affiliation: Affiliation): Promise<AxiosResponse<any>> {
    return Axios.post(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgIdentifier}/affiliations`, affiliation)
  }

  static async removeAffiliation (orgIdentifier: number, incorporationNumber: string): Promise<AxiosResponse<void>> {
    return Axios.delete(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgIdentifier}/affiliations/${incorporationNumber}`)
  }

  static async searchBusiness (businessIdentifier: string): Promise<AxiosResponse<any>> {
    return Axios.get(`${ConfigHelper.getValue('VUE_APP_LEGAL_ROOT_API')}/businesses/${businessIdentifier}`)
  }
}
