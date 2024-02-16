import { AffiliationInvitation, CreateAffiliationInvitation } from '@/models/affiliation-invitation'
import { AffiliationInvitationStatus } from '@/util/constants'
import { AffiliationInviteInfo } from '@/models/affiliation'
import { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { axios } from '@/util/http-util'

export default class AffiliationInvitationService {
  static async getAffiliationInvitations (orgIdentifier: number | string, status: AffiliationInvitationStatus = null)
    : Promise<AffiliationInviteInfo[]> {
    try {
      let params: any = { orgId: orgIdentifier, businessDetails: true }
      if (status) {
        params = { ...params, status: status }
      }
      const response = await axios.get(`${ConfigHelper.getAuthAPIUrl()}/affiliationInvitations`, { params: params })
      return response.data.affiliationInvitations
    } catch (err) {
      // eslint-disable-line no-console
      console.log(err)
      return null
    }
  }
  static async removeAffiliationInvitation (affiliationInvitationId: number) : Promise<boolean> {
    try {
      await axios.delete(`${ConfigHelper.getAuthAPIUrl()}/affiliationInvitations/${affiliationInvitationId}`)
      return true
    } catch (err) {
      // eslint-disable-line no-console
      console.log(err)
      return false
    }
  }
  static async createInvitation (payload: CreateAffiliationInvitation): Promise<AxiosResponse<any>> {
    return axios.post(`${ConfigHelper.getAuthAPIUrl()}/affiliationInvitations`, payload)
  }
  static async updateInvitation (id: string): Promise<AxiosResponse<any>> {
    return axios.patch(`${ConfigHelper.getAuthAPIUrl()}/affiliationInvitations/${id}`, {})
  }
  static async acceptInvitation (id: string, invitationToken: string): Promise<AxiosResponse<AffiliationInvitation>> {
    return axios.put(`${ConfigHelper.getAuthAPIUrl()}/affiliationInvitations/${id}/token/${invitationToken}`)
  }
}
