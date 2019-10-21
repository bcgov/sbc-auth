import Axios, { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '../models/contact'
import { Organizations } from '@/models/Organization'
import { User } from '../models/user'

export default class UserService {
  static async getUserProfile (identifier: string): Promise<AxiosResponse<User>> {
    return Axios.get(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/users/${identifier}`)
  }

  static async createUserProfile (): Promise<AxiosResponse<User>> {
    return Axios.post(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/users`, {})
  }

  static async createContact (contact:Contact): Promise<AxiosResponse<Contact>> {
    return Axios.post(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/users/contacts`, contact)
  }

  static async getOrganizations (): Promise<AxiosResponse<Organizations>> {
    return Axios.get(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/users/orgs`)
  }
}
