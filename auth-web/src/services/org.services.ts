import Axios, { AxiosResponse } from 'axios'
import configHelper from '@/util/config-helper'
import { Members, Member } from '@/models/Organization'
import { Invitations } from '@/models/Invitation'

export default class OrgService {
  public static async getOrgMembers (orgId: number): Promise<AxiosResponse<Members>> {
    return Axios.get(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgId}/members`)
  }

  public static async getOrgInvitations (orgId: number): Promise<AxiosResponse<Invitations>> {
    return Axios.get(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgId}/invitations`)
  }

  public static async removeMember (orgId: number, memberId: number): Promise<AxiosResponse<Member>> {
    return Axios.delete(`${configHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgId}/members/${memberId}`)
  }
}
