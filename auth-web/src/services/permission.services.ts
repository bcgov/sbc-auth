import Axios, { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { addAxiosInterceptors } from 'sbc-common-components/src/util/interceptors'

const axios = addAxiosInterceptors(Axios.create())

export default class PermissionService {
  static async getPermissions (role: string): Promise<AxiosResponse<String[]>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/permissions/${role}`)
  }
}
