import {
  AccountType,
  Configurations,
  DissolutionStatistics,
  ProductCode,
  Products,
  ProductsRequestBody,
  SafeListEmailsRequestBody
} from '@/models/Staff'
import { OrgFilterParams, OrgList, Organizations } from '@/models/Organization'
import { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { InvoluntaryDissolutionConfigNames } from '@/util/constants'
import { SafeEmail } from '@/models/safe-email'
import { axios } from '@/util/http-util'

export default class StaffService {
  static async getProducts (): Promise<AxiosResponse<ProductCode[]>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/codes/product_codes`)
  }

  static async getAccountTypes (): Promise<AxiosResponse<AccountType[]>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/codes/org_types`)
  }

  static async getStaffOrgs (status?: string): Promise<AxiosResponse<Organizations>> {
    const params = new URLSearchParams()
    // params.append('access_type', 'REGULAR_BCEID,EXTRA_PROVINCIAL')
    if (status) {
      params.append('status', status)
    }
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/orgs`, { params })
  }

  public static async addProducts (orgIdentifier: number, productsRequestBody: ProductsRequestBody):
    Promise<AxiosResponse<Products>> {
    return axios.post(`${ConfigHelper.getAuthAPIUrl()}/orgs/${orgIdentifier}/products`, productsRequestBody)
  }

  static async searchOrgs (orgFilter?: OrgFilterParams): Promise<AxiosResponse<OrgList>> {
    const params = new URLSearchParams()
    for (const key in orgFilter) {
      if (!orgFilter[key]) {
        continue
      }
      if (key === 'accessType') {
        orgFilter.accessType.forEach(accessType => params.append('accessType', accessType))
      } else if (key === 'statuses') {
        orgFilter.statuses.forEach(status => params.append('status', status))
      } else {
        params.append(key, orgFilter[key])
      }
    }
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/orgs`, { params })
  }

  static async getSafeEmails (): Promise<AxiosResponse<SafeEmail[]>> {
    try {
      const response: AxiosResponse<SafeEmail[]> = await axios.get(`${ConfigHelper.getNotifiyAPIUrl()}/safe_list`)
      if (response.status === 200 && response.data) {
        return response
      } else {
        throw new Error('Failed to fetch safe emails')
      }
    } catch (error) {
      const errMsg = `Failed to fetch safe emails, ${error}`
      console.error(errMsg)
      throw Error(errMsg)
    }
  }

  static async getInvoluntaryDissolutionBatchSize (): Promise<AxiosResponse<Configurations>> {
    return axios.get(`${ConfigHelper.getLegalAPIV2Url()}/admin/configurations`, {
      params: { names: InvoluntaryDissolutionConfigNames.NUM_DISSOLUTIONS_ALLOWED }
    })
  }

  static async getDissolutionStatistics (): Promise<AxiosResponse<DissolutionStatistics>> {
    return axios.get(`${ConfigHelper.getLegalAPIV2Url()}/admin/dissolutions/statistics`)
  }

  static async updateInvoluntaryDissolutionConfigurations (configurations: Configurations): Promise<AxiosResponse<Configurations>> {
    return axios.put(`${ConfigHelper.getLegalAPIV2Url()}/admin/configurations`, configurations)
  }

  static async deleteSafeEmail (email: string): Promise<AxiosResponse> {
    try {
      const response: AxiosResponse = await axios.delete(`${ConfigHelper.getNotifiyAPIUrl()}/safe_list/${email}`)
      if (response.status === 200) {
        return response
      } else {
        throw new Error(`Failed to delete safe email ${email}`)
      }
    } catch (error) {
      const errMsg = `Unable to delete ${email}, ${error}`
      console.error(errMsg)
      throw Error(errMsg)
    }
  }

  static async addSafeEmail (safeListEmailsRequestBody: SafeListEmailsRequestBody): Promise<AxiosResponse<SafeEmail[]>> {
    return axios.post(`${ConfigHelper.getNotifiyAPIUrl()}/safe_list`, safeListEmailsRequestBody)
  }
}
