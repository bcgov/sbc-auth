import { Business } from '@/models/business'
import Axios, { AxiosPromise, AxiosResponse } from 'axios'
import configHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import { Org } from '@/models/org'
import { Entity } from '@/models/entity'
import { Affiliation } from '@/models/affiliation'

interface BusinessService {
  getBusiness: (businessNumber: string) => Promise<AxiosResponse<Business>>
  createBusiness: (business: Business) => Promise<AxiosResponse<Business>>
  addContact: (business: Business, contact: Contact) => Promise<AxiosResponse<Business>>
  updateContact: (business: Business, coontact: Contact) => Promise<AxiosResponse<Business>>
  getOrgs: () => Promise<AxiosResponse<any>>
  createOrg: (org: Org) => Promise<AxiosResponse<Org>>
  createAffiliation: (orgIdentifier: string, affiliation: Affiliation) => Promise<AxiosResponse<Affiliation>>
  removeAffiliation: (orgIdentifier: string, incorporationNumber: string) => Promise<AxiosResponse<void>>
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
  async createOrg (org: Org): Promise<AxiosResponse<Org>> {
    return Axios.post(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs`, org)
  },
  async createAffiliation (orgIdentifier: string, affiliation: Affiliation): Promise<AxiosResponse<any>> {
    return Axios.post(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgIdentifier}/affiliations`, affiliation)
  },
  async removeAffiliation (orgIdentifier: string, incorporationNumber: string): Promise<AxiosResponse<void>> {
    return Axios.delete(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgIdentifier}/affiliations/${incorporationNumber}`)
  }
} as BusinessService
