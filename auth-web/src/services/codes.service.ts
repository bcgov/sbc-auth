import { AxiosResponse } from 'axios'
import { Code } from '@/models/Code'
import ConfigHelper from '@/util/config-helper'
import { axios } from '@/util/http-util'

export default class CodesService {
  public static async getCodes (codeType: string): Promise<AxiosResponse<Code[]>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/codes/${codeType}`)
  }
}
