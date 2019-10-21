import Axios, { AxiosResponse } from 'axios'
import { Member, Members } from '@/models/Organization'
import ConfigHelper from '@/util/config-helper'
import { Invitations } from '@/models/Invitation'

export default class OrgService {
  public static async getOrgMembers (orgId: number): Promise<AxiosResponse<Members>> {
    return Axios.get(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgId}/members`)
  }

  public static async getOrgInvitations (orgId: number, status: string = 'ALL'): Promise<AxiosResponse<Invitations>> {
    return Axios.get(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgId}/invitations?status=${status}`)
  }

  public static async removeMember (orgId: number, memberId: number): Promise<AxiosResponse<Member>> {
    return Axios.delete(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgId}/members/${memberId}`)
  }

  public static async updateMember (orgId: number, memberId: number, role: string): Promise<AxiosResponse<Member>> {
    return Axios.patch(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgId}/members/${memberId}`, { role })
  }
}
