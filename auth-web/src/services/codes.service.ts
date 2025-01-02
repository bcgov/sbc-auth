import { AxiosResponse } from 'axios'
import { Code } from '@/models/Code'
import ConfigHelper from '@/util/config-helper'
import { axios } from '@/util/http-util'

export default class CodesService {
  public static async getCodes (codeType: string): Promise<AxiosResponse<Code[]>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/codes/${codeType}`)
  }

  public static async getPaymentMethods (productCode?: string): Promise<AxiosResponse<{[key: string]: string[]}>> {
    const url = productCode
      ? `${ConfigHelper.getPayAPIURL()}/codes/valid_payment_methods/${productCode}`
      : `${ConfigHelper.getPayAPIURL()}/codes/valid_payment_methods`
    return axios.get(url)
  }
}
