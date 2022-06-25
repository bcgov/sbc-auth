import { AccountType, ProductCode, Products, ProductsRequestBody } from '@/models/Staff'
import { OrgFilterParams, OrgList, Organizations } from '@/models/Organization'
import { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { axios } from '@/util/http-util.ts'

export default class StaffService {
  static async getProducts (): Promise<AxiosResponse<ProductCode[]>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/codes/product_codes`)
  }

  static async getAccountTypes (): Promise<AxiosResponse<AccountType[]>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/codes/org_types`)
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
    for (const key in orgFilter) {
      if (!orgFilter[key]) {
        continue
      }
      if (key === 'status') {
        orgFilter.statuses.forEach(status => params.append('status', status))
      } else {
        params.append(key, orgFilter[key])
      }
    }
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/orgs`, { params })
  }
}
