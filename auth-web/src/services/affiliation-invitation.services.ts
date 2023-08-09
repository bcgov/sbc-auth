import { AffiliationInvitation, CreateAffiliationInvitation } from '@/models/affiliation-invitation'
import { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { axios } from '@/util/http-util'

// For Magic Link and Delegation. UNTESTED until backend is finalized.
export default class AffiliationInvitationService {
  public static async getInvitations (orgId: string): Promise<AxiosResponse<AffiliationInvitation>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/affiliationInvitations?orgId=${orgId}`)
  }
  public static async createInvitation (payload: CreateAffiliationInvitation): Promise<AxiosResponse<any>> {
    return axios.post(`${ConfigHelper.getAuthAPIUrl()}/affiliationInvitations`, payload)
  }
  // Future - Unused for now-  also more to add than this.
  public static async updateInvitation (orgId: string): Promise<AxiosResponse<any>> {
    return axios.patch(`${ConfigHelper.getAuthAPIUrl()}/affiliationInvitations`)
  }
  public static async acceptInvitation (invitationId: string): Promise<AxiosResponse<any>> {
    return axios.put(`${ConfigHelper.getAuthAPIUrl()}/affiliationInvitations/${invitationId}`)
  }
}
