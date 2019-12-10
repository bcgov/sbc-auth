import Axios, { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import { Organizations } from '@/models/Organization'
import { User } from '@/models/user'

export default class UserService {
  static async getUserProfile (identifier: string): Promise<AxiosResponse<User>> {
    return Axios.get(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/users/${identifier}`)
  }

  static async syncUserProfile (): Promise<AxiosResponse<User>> {
    return Axios.post(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/users`, {})
  }

  static async createContact (contact:Contact): Promise<AxiosResponse<Contact>> {
    return Axios.post(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/users/contacts`, contact)
  }

  static async updateContact (contact: Contact): Promise<AxiosResponse<Contact>> {
    return Axios.put(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/users/contacts`, contact)
  }

  static async getOrganizations (): Promise<AxiosResponse<Organizations>> {
    return Axios.get(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/users/orgs`)
  }

  static async updateUserTerms (identifier: string, termsversion: string,
    istermsaccepted: boolean): Promise<AxiosResponse<User>> {
    return Axios.patch(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/users/${identifier}`, { termsversion: termsversion,
      istermsaccepted: istermsaccepted })
  }

  static async deactivateUser (): Promise<AxiosResponse<User>> {
    return Axios.delete(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/users/@me`)
  }
}
