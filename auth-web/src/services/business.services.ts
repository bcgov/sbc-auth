import { Business } from '@/models/business'
import Axios, { AxiosPromise, AxiosResponse } from 'axios'
import configHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import { Organization } from '@/models/Organization'
import { Affiliation } from '@/models/affiliation'

interface BusinessService {
  getBusiness: (businessNumber: string) => Promise<AxiosResponse<Business>>
  createBusiness: (business: Business) => Promise<AxiosResponse<Business>>
  addContact: (business: Business, contact: Contact) => Promise<AxiosResponse<Business>>
  updateContact: (business: Business, coontact: Contact) => Promise<AxiosResponse<Business>>
  getOrgs: () => Promise<AxiosResponse<any>>
  createOrg: (org: Organization) => Promise<AxiosResponse<Organization>>
  createAffiliation: (orgIdentifier: string, affiliation: Affiliation) => Promise<AxiosResponse<Affiliation>>
  removeAffiliation: (orgIdentifier: string, incorporationNumber: string) => Promise<AxiosResponse<void>>
  // Following searchBusiness will search data from legal-api.
  searchBusiness: (businessNumber: string) => Promise<AxiosResponse<any>>
}

export default {
  async getBusiness (businessIdentifier: string): Promise<AxiosResponse<Business>> {
    return Axios.get(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/entities/${businessIdentifier}`)
  },
  async createBusiness (business: Business): Promise<AxiosResponse<Business>> {
    return Axios.post(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/entities`, business)
  },
  async addContact (business: Business, contact: Contact): Promise<AxiosResponse<Business>> {
    return Axios.post(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/entities/${business.businessIdentifier}/contacts`, contact)
  },
  async updateContact (business: Business, contact: Contact): Promise<AxiosResponse<Business>> {
    return Axios.put(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/entities/${business.businessIdentifier}/contacts`, contact)
  },
  async getOrgs (): Promise<AxiosResponse<any>> {
    return Axios.get(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/users/orgs`)
  },
  async createOrg (org: Organization): Promise<AxiosResponse<Organization>> {
    return Axios.post(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs`, org)
  },
  async createAffiliation (orgIdentifier: string, affiliation: Affiliation): Promise<AxiosResponse<any>> {
    return Axios.post(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgIdentifier}/affiliations`, affiliation)
  },
  async removeAffiliation (orgIdentifier: string, incorporationNumber: string): Promise<AxiosResponse<void>> {
    return Axios.delete(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgIdentifier}/affiliations/${incorporationNumber}`)
  },
  async searchBusiness (businessIdentifier: string): Promise<AxiosResponse<any>> {
    return Axios.get(`${configHelper.getValue('VUE_APP_LEGAL_ROOT_API')}/businesses/${businessIdentifier}`)
  }
} as BusinessService
