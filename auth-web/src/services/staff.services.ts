import { AccountType, ProductCode, Products, ProductsRequestBody } from '@/models/Staff'
import Axios, { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { addAxiosInterceptors } from 'sbc-common-components/src/util/interceptors'

const axios = addAxiosInterceptors(Axios.create())

export default class StaffService {
  static async getProducts (): Promise<AxiosResponse<ProductCode[]>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/codes/product_code`)
  }

  static async getAccountTypes (): Promise<AxiosResponse<AccountType[]>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/codes/org_type`)
  }

  public static async addProducts (orgIdentifier: number, productsRequestBody: ProductsRequestBody): Promise<AxiosResponse<Products>> {
    return axios.post(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgIdentifier}/products`, productsRequestBody)
  }
}
