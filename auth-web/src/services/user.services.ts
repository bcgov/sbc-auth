import Axios, { AxiosResponse } from 'axios'
import { Contact, Contacts } from '@/models/contact'
import ConfigHelper from '@/util/config-helper'
import { Organizations } from '@/models/Organization'
import { User } from '@/models/user'

export default class UserService {
  static async getUserProfile (identifier: string): Promise<AxiosResponse<User>> {
    return Axios.get(`${ConfigHelper.getAuthAPIUrl()}/users/${identifier}`)
  }

  static async syncUserProfile (): Promise<AxiosResponse<User>> {
    return Axios.post(`${ConfigHelper.getAuthAPIUrl()}/users`, {})
  }

  static async createContact (contact: Contact): Promise<AxiosResponse<Contact>> {
    return Axios.post(`${ConfigHelper.getAuthAPIUrl()}/users/contacts`, contact)
  }

  static async getContacts (): Promise<AxiosResponse<Contacts>> {
    return Axios.get(`${ConfigHelper.getAuthAPIUrl()}/users/contacts`)
  }

  static async updateContact (contact: Contact): Promise<AxiosResponse<Contact>> {
    return Axios.put(`${ConfigHelper.getAuthAPIUrl()}/users/contacts`, contact)
  }

  static async getOrganizations (): Promise<AxiosResponse<Organizations>> {
    return Axios.get(`${ConfigHelper.getAuthAPIUrl()}/users/orgs`)
  }

  static async updateUserTerms (identifier: string, termsVersion: string,
    isTermsAccepted: boolean): Promise<AxiosResponse<User>> {
    return Axios.patch(`${ConfigHelper.getAuthAPIUrl()}/users/${identifier}`, {
      termsversion: termsVersion,
      istermsaccepted: isTermsAccepted }
    )
  }

  static async deactivateUser (): Promise<AxiosResponse<User>> {
    return Axios.delete(`${ConfigHelper.getAuthAPIUrl()}/users/@me`)
  }
}
