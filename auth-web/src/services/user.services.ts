import Axios, { AxiosPromise, AxiosResponse } from 'axios'
import configHelper from '@/util/config-helper'

interface UserService {
  getUserProfile: (identifier: string) => Promise<AxiosResponse<any>>
}

export default {
  async getUserProfile (identifier: string): Promise<AxiosResponse<any>> {
    return Axios.get(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/users/${identifier}`)
  }
} as UserService
