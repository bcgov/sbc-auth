import { AccountType, ProductCode, Products, ProductsRequestBody } from '@/models/Staff'
import Axios, { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { Organizations } from '@/models/Organization'
import { addAxiosInterceptors } from 'sbc-common-components/src/util/interceptors'

const axios = addAxiosInterceptors(Axios.create())

export default class StaffService {
  static async getProducts (): Promise<AxiosResponse<ProductCode[]>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/codes/product_code`)
  }

  static async getAccountTypes (): Promise<AxiosResponse<AccountType[]>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/codes/org_type`)
  }

  static async getStaffOrgs (status?: string): Promise<AxiosResponse<Organizations>> {
    let params = new URLSearchParams()
    params.append('access_type', 'REGULAR_BCEID,EXTRA_PROVINCIAL')
    if (status) {
      params.append('status', status)
    }
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/orgs`, { params })
  }

  public static async addProducts (orgIdentifier: number, productsRequestBody: ProductsRequestBody): Promise<AxiosResponse<Products>> {
    return axios.post(`${ConfigHelper.getAuthAPIUrl()}/orgs/${orgIdentifier}/products`, productsRequestBody)
  }
}
