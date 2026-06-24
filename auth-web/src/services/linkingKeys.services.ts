import { AccountLinkingKey, AccountLinkingKeysResponse } from '@/models/vendorConnection'

import { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { axios } from '@/util/http-util'

export default class LinkingKeysService {
  public static async getOrgLinkingKeys (orgId: number): Promise<AxiosResponse<AccountLinkingKeysResponse>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/orgs/${orgId}/linking-keys`)
  }

  public static async revokeOrgLinkingKey (linkingKeyDetails): Promise<AxiosResponse<Record<string, never>>> {
    const { orgId, keyId } = linkingKeyDetails
    return axios.delete(`${ConfigHelper.getAuthAPIUrl()}/orgs/${orgId}/linking-keys/${keyId}`)
  }

  public static async extendOrgLinkingKey (linkingKeyDetails): Promise<AxiosResponse<AccountLinkingKey>> {
    const { orgId, keyId } = linkingKeyDetails
    return axios.patch(`${ConfigHelper.getAuthAPIUrl()}/orgs/${orgId}/linking-keys/${keyId}`, {
      action: 'extend'
    })
  }
}
