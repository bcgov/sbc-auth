import Axios, { AxiosResponse } from 'axios'
import configHelper from '@/util/config-helper'
import { Invitation } from '@/models/Invitation'
import { EmptyResponse } from '@/models/global'

export default class InvitationService {
  public static async createInvitation (invitation: Invitation): Promise<AxiosResponse<Invitation>> {
    return Axios.post(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/invitations`, invitation)
  }

  public static async resendInvitation (invitation: Invitation): Promise<AxiosResponse<Invitation>> {
    return Axios.patch(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/invitations/${invitation.id}`, invitation)
  }

  public static async deleteInvitation (invitationId: number): Promise<AxiosResponse<Invitation>> {
    return Axios.delete(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/invitations/${invitationId}`)
  }

  public static async validateToken (token: string): Promise<AxiosResponse<EmptyResponse>> {
    return Axios.get(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/invitations/tokens/${token}`)
  }

  public static async acceptInvitation (token: string): Promise<AxiosResponse<Invitation>> {
    return Axios.put(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/invitations/tokens/${token}`, {})
  }
}
