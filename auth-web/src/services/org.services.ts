import { Affiliation, CreateRequestBody as CreateAffiliationRequestBody, CreateNRAffiliationRequestBody } from '@/models/affiliation'
import Axios, { AxiosResponse } from 'axios'
import { CreateRequestBody as CreateOrganizationRequestBody, Member, Members, Organization, UpdateMemberPayload } from '@/models/Organization'
import { Actions } from '@/util/constants'
import { Address } from '@/models/address'
import { AffidavitInformation } from '@/models/affidavit'
import { Businesses } from '@/models/business'
import ConfigHelper from '@/util/config-helper'
import { Invitations } from '@/models/Invitation'
import { PaymentSettings } from '@/models/PaymentSettings'
import { addAxiosInterceptors } from 'sbc-common-components/src/util/interceptors'

const axios = addAxiosInterceptors(Axios.create())

export default class OrgService {
  public static async getOrganization (orgId: number): Promise<AxiosResponse<Organization>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/orgs/${orgId}`)
  }

  public static async getContactForOrg (orgId: number): Promise<Address> {
    const response = await axios.get(`${ConfigHelper.getAuthAPIUrl()}/orgs/${orgId}/contacts`)
    // for now it returns only address , can return the all the contacts as well
    return response.data.contacts[0]
  }

  public static async isOrgNameAvailable (orgName: string): Promise<AxiosResponse> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/orgs?name=${orgName}`)
  }

  public static async getOrgMembers (orgId: number, status: string): Promise<AxiosResponse<Members>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/orgs/${orgId}/members?status=${status}`)
  }

  public static async getPaymentSettings (orgId: number): Promise<AxiosResponse<PaymentSettings>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/orgs/${orgId}/payment_settings`)
  }

  public static async getOrgInvitations (orgId: number, status: string = 'ALL'): Promise<AxiosResponse<Invitations>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/orgs/${orgId}/invitations?status=${status}`)
  }

  public static async deactivateOrg (orgId: number): Promise<AxiosResponse<void>> {
    return axios.delete(`${ConfigHelper.getAuthAPIUrl()}/orgs/${orgId}`)
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

  public static async upgradeOrDowngradeOrg (createRequestBody: CreateOrganizationRequestBody, orgId: number, action:Actions): Promise<AxiosResponse<Organization>> {
    return axios.put(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgId}?action=${action}`, createRequestBody)
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

  static async createNRAffiliation (orgIdentifier: number, affiliation: CreateNRAffiliationRequestBody): Promise<AxiosResponse<Affiliation>> {
    return axios.post(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgIdentifier}/affiliations?newBusiness=true`, affiliation)
  }

  static async removeAffiliation (orgIdentifier: number, incorporationNumber: string): Promise<AxiosResponse<void>> {
    return axios.delete(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgIdentifier}/affiliations/${incorporationNumber}`)
  }

  static async getAffidavitInfo (orgIdentifier: number): Promise<AxiosResponse<AffidavitInformation>> {
    return axios.get(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgIdentifier}/admins/affidavits`)
  }

  static async approvePendingOrg (orgIdentifier: number): Promise<AxiosResponse> {
    return axios.patch(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgIdentifier}/status`, { statusCode: 'APPROVED' })
  }

  static async rejectPendingOrg (orgIdentifier: number): Promise<AxiosResponse> {
    return axios.patch(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/orgs/${orgIdentifier}/status`, { statusCode: 'REJECTED' })
  }

  public static async getMemberLoginOption (orgId: number): Promise<string> {
    const response = await axios.get(`${ConfigHelper.getAuthAPIUrl()}/orgs/${orgId}/login-options`)
    return response.data?.loginOption
  }

  public static async updateMemberLoginOption (orgId: number, loginOption:string): Promise<string> {
    const response = await axios.put(`${ConfigHelper.getAuthAPIUrl()}/orgs/${orgId}/login-options`, {
      'loginOption': loginOption
    })
    return response.data?.loginOption
  }
}
