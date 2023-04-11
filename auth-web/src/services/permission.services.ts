import ConfigHelper from '@/util/config-helper'
import { axios } from '@/util/http-util'
import { AxiosResponse } from 'axios'

export default class PermissionService {
  static async getPermissions (orgStatus:string, role: string): Promise<AxiosResponse<string[]>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/permissions/${orgStatus}/${role}?case=upper`)
  }
}
