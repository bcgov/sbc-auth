import { AccountType, ProductCode, Products, ProductsRequestBody } from '@/models/Staff'
import Axios, { AxiosResponse } from 'axios'
import { OrgFilterParams, OrgList, Organizations } from '@/models/Organization'
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

  static async getStaffOrgs (status?: string): Promise<AxiosResponse<Organizations>> {
    let params = new URLSearchParams()
    // params.append('access_type', 'REGULAR_BCEID,EXTRA_PROVINCIAL')
    if (status) {
      params.append('status', status)
    }
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/orgs`, { params })
  }

  public static async addProducts (orgIdentifier: number, productsRequestBody: ProductsRequestBody): Promise<AxiosResponse<Products>> {
    return axios.post(`${ConfigHelper.getAuthAPIUrl()}/orgs/${orgIdentifier}/products`, productsRequestBody)
  }

  static async searchOrgs (orgFilter?: OrgFilterParams): Promise<AxiosResponse<OrgList>> {
    let params = new URLSearchParams()
    if (orgFilter.status) {
      params.append('status', orgFilter.status)
    }
    if (orgFilter.name) {
      params.append('name', orgFilter.name)
    }
    if (orgFilter.pageNumber) {
      params.append('page', orgFilter.pageNumber.toString())
    }
    if (orgFilter.pageLimit) {
      params.append('limit', orgFilter.pageLimit.toString())
    }

    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/orgs`, { params })
  }
}
