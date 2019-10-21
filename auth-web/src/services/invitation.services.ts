import Axios, { AxiosResponse } from 'axios'
import ConfigHelper from '@/util/config-helper'
import { EmptyResponse } from '@/models/global'
import { Invitation, CreateRequestBody } from '@/models/Invitation'

export default class InvitationService {
  public static async createInvitation (invitation: CreateRequestBody): Promise<AxiosResponse<Invitation>> {
    return Axios.post(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/invitations`, invitation)
  }

  public static async resendInvitation (invitation: Invitation): Promise<AxiosResponse<Invitation>> {
    return Axios.patch(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/invitations/${invitation.id}`, invitation)
  }

  public static async deleteInvitation (invitationId: number): Promise<AxiosResponse<Invitation>> {
    return Axios.delete(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/invitations/${invitationId}`)
  }

  public static async validateToken (token: string): Promise<AxiosResponse<EmptyResponse>> {
    return Axios.get(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/invitations/tokens/${token}`)
  }

  public static async acceptInvitation (token: string): Promise<AxiosResponse<Invitation>> {
    return Axios.put(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/invitations/tokens/${token}`, {})
  }
}
