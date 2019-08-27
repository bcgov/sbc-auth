import Axios, { AxiosPromise, AxiosResponse } from 'axios'
import configHelper from '@/util/config-helper'
import { User } from '../models/user'
import { Contact } from '../models/contact'

interface UserService {
  getUserProfile: (identifier: string) => Promise<AxiosResponse<User>>
  createUserProfile: () => Promise<AxiosResponse<User>>
  createContact: (contact:Contact) => Promise<AxiosResponse<Contact>>
}

export default {
  async getUserProfile (identifier: string): Promise<AxiosResponse<User>> {
    return Axios.get(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/users/${identifier}`)
  },
  async createUserProfile (): Promise<AxiosResponse<User>> {
    return Axios.post(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/users`, {})
  },
  async createContact (contact:Contact): Promise<AxiosResponse<Contact>> {
    return Axios.post(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/users/contacts`, contact)
  }

} as UserService
