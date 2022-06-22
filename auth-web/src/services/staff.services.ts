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
    if (orgFilter.statuses) {
      orgFilter.statuses.forEach(status =>
        params.append('status', status))
    }
    if (orgFilter.name) {
      params.append('name', orgFilter.name)
    }
    if (orgFilter.branchName) {
      params.append('branchName', orgFilter.branchName)
    }
    if (orgFilter.id) {
      params.append('id', orgFilter.id)
    }
    if (orgFilter.decisionMadeBy) {
      params.append('decisionMadeBy', orgFilter.decisionMadeBy)
    }
    if (orgFilter.orgType) {
      params.append('orgType', orgFilter.orgType)
    }
    if (orgFilter.accessType) {
      params.append('accessType', orgFilter.accessType)
    }
    if (orgFilter.firstName) {
      params.append('firstName', orgFilter.firstName)
    }
    if (orgFilter.lastName) {
      params.append('lastName', orgFilter.lastName)
    }
    if (orgFilter.emailAddress) {
      params.append('emailAddress', orgFilter.emailAddress)
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
