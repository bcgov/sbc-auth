import { CreateRequestBody, Invitation } from '@/models/Invitation'
import { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { EmptyResponse } from '@/models/global'
import { axios } from '@/util/http-util'

export default class InvitationService {
  public static async createInvitation (invitation: CreateRequestBody): Promise<AxiosResponse<Invitation>> {
    return axios.post(`${ConfigHelper.getAuthAPIUrl()}/invitations`, invitation)
  }

  public static async resendInvitation (invitation: Invitation): Promise<AxiosResponse<Invitation>> {
    return axios.patch(`${ConfigHelper.getAuthAPIUrl()}/invitations/${invitation.id}`, invitation)
  }

  public static async deleteInvitation (invitationId: number): Promise<AxiosResponse<Invitation>> {
    return axios.delete(`${ConfigHelper.getAuthAPIUrl()}/invitations/${invitationId}`)
  }

  public static async validateToken (token: string): Promise<AxiosResponse<EmptyResponse>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/invitations/tokens/${token}`)
  }

  public static async acceptInvitation (token: string): Promise<AxiosResponse<Invitation>> {
    return axios.put(`${ConfigHelper.getAuthAPIUrl()}/invitations/tokens/${token}`, {})
  }
}
