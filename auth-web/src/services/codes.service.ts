import { AxiosResponse } from 'axios'
import { Code } from '@/models/Code'
import ConfigHelper from '@/util/config-helper'
import { axios } from '@/util/http-util'

export default class CodesService {
  public static async getCodes (codeType: string): Promise<AxiosResponse<Code[]>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/codes/${codeType}`)
  }

  public static async getProductPaymentMethods (productCode?: string): Promise<any> {
    let url = `${ConfigHelper.getPayAPIURL()}/codes/valid_payment_methods`
    if (productCode) {
      url += `/${productCode}`
    }
    try {
      const response = await axios.get(url)
      return response.data
    } catch (error) {
      // eslint-disable-line no-console
      console.log(error)
      return null
    }
  }
}
