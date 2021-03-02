import { AxiosResponse } from 'axios'
import { Code } from '@/models/code'
import ConfigHelper from '@/util/config-helper'
import { axios } from '@/util/http-util.ts'

export default class CodesService {
  public static async getSuspensionReasonCodes (codeType: string): Promise<AxiosResponse<Code[]>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/codes/${codeType}`)
  }
}
