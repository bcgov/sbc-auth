import Axios, { AxiosResponse } from 'axios'
import { Contact, Contacts } from '@/models/contact'
import { Member, Organizations } from '@/models/Organization'
import { User, UserProfileRequestBody } from '@/models/user'
import ConfigHelper from '@/util/config-helper'
import { addAxiosInterceptors } from 'sbc-common-components/src/util/interceptors'

const axios = addAxiosInterceptors(Axios.create())

export default class UserService {
  static async getUserProfile (identifier: string): Promise<AxiosResponse<User>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/users/${identifier}`)
  }

  static async syncUserProfile (): Promise<AxiosResponse<User>> {
    return axios.post(`${ConfigHelper.getAuthAPIUrl()}/users`, {})
  }

  static async createContact (contact: Contact): Promise<AxiosResponse<Contact>> {
    return axios.post(`${ConfigHelper.getAuthAPIUrl()}/users/contacts`, contact)
  }

  static async getContacts (): Promise<AxiosResponse<Contacts>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/users/contacts`)
  }

  static async updateContact (contact: Contact): Promise<AxiosResponse<Contact>> {
    return axios.put(`${ConfigHelper.getAuthAPIUrl()}/users/contacts`, contact)
  }

  static async getOrganizations (): Promise<AxiosResponse<Organizations>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/users/orgs`)
  }

  static async updateUserTerms (identifier: string, termsVersion: string,
    isTermsAccepted: boolean): Promise<AxiosResponse<User>> {
    return axios.patch(`${ConfigHelper.getAuthAPIUrl()}/users/${identifier}`, {
      termsversion: termsVersion,
      istermsaccepted: isTermsAccepted }
    )
  }

  static async deactivateUser (): Promise<AxiosResponse<User>> {
    return axios.delete(`${ConfigHelper.getAuthAPIUrl()}/users/@me`)
  }

  static async getMembership (orgId: number): Promise<AxiosResponse<Member>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/users/orgs/${orgId}/membership`)
  }

  static async createUserProfile (token: string, userProfile: UserProfileRequestBody): Promise<AxiosResponse<any>> {
    return axios.post(`${ConfigHelper.getAuthAPIUrl()}/users/${token}`, userProfile)
  }
}
