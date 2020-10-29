import { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { axios } from '@/util/http-util.ts'

export default class PermissionService {
  static async getPermissions (role: string): Promise<AxiosResponse<string[]>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/permissions/${role}`)
  }
}
