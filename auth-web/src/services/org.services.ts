import { Affiliation, CreateRequestBody as CreateAffiliationRequestBody } from '@/models/affiliation'
import Axios, { AxiosResponse } from 'axios'
import { CreateRequestBody as CreateOrganizationRequestBody, Member, Members, Organization, UpdateMemberPayload } from '@/models/Organization'
import { Businesses } from '@/models/business'
import ConfigHelper from '@/util/config-helper'
import { Invitations } from '@/models/Invitation'
import { addAxiosInterceptors } from 'sbc-common-components/src/util/interceptors'

const axios = addAxiosInterceptors(Axios.create())

export default class OrgService {
  public static async getOrganization (orgId: number): Promise<AxiosResponse<Organization>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/orgs/${orgId}`)
  }

  public static async getOrgMembers (orgId: number, status: string): Promise<AxiosResponse<Members>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/orgs/${orgId}/members?status=${status}`)
  }

  public static async getOrgInvitations (orgId: number, status: string = 'ALL'): Promise<AxiosResponse<Invitations>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/orgs/${orgId}/invitations?status=${status}`)
  }

  public static async leaveOrg (orgId: number, memberId: number): Promise<AxiosResponse<Member>> {
    return axios.delete(`${ConfigHelper.getAuthAPIUrl()}/orgs/${orgId}/members/${memberId}`)
  }

  public static async updateMember (orgId: number, updatePayload: UpdateMemberPayload): Promise<AxiosResponse<Member>> {
    return axios.patch(`${ConfigHelper.getAuthAPIUrl()}/orgs/${orgId}/members/${updatePayload.memberId}`,
      { role: updatePayload.role, status: updatePayload.status, notifyUser: updatePayload.notifyUser })
  }

  public static async createOrg (createRequestBody: CreateOrganizationRequestBody): Promise<AxiosResponse<Organization>> {
    return axios.post(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs`, createRequestBody)
  }

  public static async updateOrg (orgId: number, createRequestBody: CreateOrganizationRequestBody): Promise<AxiosResponse<Organization>> {
    return axios.put(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgId}`, createRequestBody)
  }

  static async getAffiliatiatedEntities (orgIdentifier: number): Promise<AxiosResponse<Businesses>> {
    return axios.get(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgIdentifier}/affiliations`)
  }

  static async createAffiliation (orgIdentifier: number, affiliation: CreateAffiliationRequestBody): Promise<AxiosResponse<Affiliation>> {
    return axios.post(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgIdentifier}/affiliations`, affiliation)
  }

  static async removeAffiliation (orgIdentifier: number, incorporationNumber: string): Promise<AxiosResponse<void>> {
    return axios.delete(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgIdentifier}/affiliations/${incorporationNumber}`)
  }
}
