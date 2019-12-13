import Axios, { AxiosResponse } from 'axios'
import { CreateRequestBody, Member, Members, Organization, UpdateMemberPayload } from '@/models/Organization'
import ConfigHelper from '@/util/config-helper'
import { Invitations } from '@/models/Invitation'

export default class OrgService {
  public static async getOrganization (orgId: number): Promise<AxiosResponse<Organization>> {
    return Axios.get(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgId}`)
  }

  public static async getOrgMembers (orgId: number, status: string): Promise<AxiosResponse<Members>> {
    return Axios.get(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgId}/members?status=${status}`)
  }

  public static async getOrgInvitations (orgId: number, status: string = 'ALL'): Promise<AxiosResponse<Invitations>> {
    return Axios.get(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgId}/invitations?status=${status}`)
  }

  public static async leaveOrg (orgId: number, memberId: number): Promise<AxiosResponse<Member>> {
    return Axios.delete(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgId}/members/${memberId}`)
  }

  public static async updateMember (orgId: number, updatePayload: UpdateMemberPayload): Promise<AxiosResponse<Member>> {
    return Axios.patch(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgId}/members/${updatePayload.memberId}`,
      { role: updatePayload.role, status: updatePayload.status, notifyUser: updatePayload.notifyUser })
  }

  public static async createOrg (createRequestBody: CreateRequestBody): Promise<AxiosResponse<Organization>> {
    return Axios.post(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs`, createRequestBody)
  }
}
