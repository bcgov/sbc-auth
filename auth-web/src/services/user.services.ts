import { AddUsersToOrgBody, BulkUserResponseBody, Member, Organizations, RoleInfo } from '@/models/Organization'
import Axios, { AxiosResponse } from 'axios'
import { Contact, Contacts } from '@/models/contact'
import { NotaryContact, NotaryInformation } from '@/models/notary'
import { User, UserProfileRequestBody } from '@/models/user'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { addAxiosInterceptors } from 'sbc-common-components/src/util/interceptors'

const axios = addAxiosInterceptors(Axios.create())

export default class UserService {
  static async getUserProfile (identifier: string): Promise<AxiosResponse<User>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/users/${identifier}`)
  }

  static async getRoles (): Promise<AxiosResponse<RoleInfo[]>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/codes/membership_type`)
  }

  static async syncUserProfile (): Promise<AxiosResponse<User>> {
    return axios.post(`${ConfigHelper.getAuthAPIUrl()}/users`, {})
  }

  // for bceid users ;the firstname and lastname has to be updated
  static async updateUserProfile (firstName:string, lastName:string): Promise<AxiosResponse<User>> {
    return axios.post(`${ConfigHelper.getAuthAPIUrl()}/users`, { firstName: firstName, lastName: lastName })
  }

  static async createContact (contact: Contact): Promise<AxiosResponse<Contact>> {
    return axios.post(`${ConfigHelper.getAuthAPIUrl()}/users/contacts`, contact)
  }

  static async getContacts (): Promise<AxiosResponse<Contacts>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/users/contacts`)
  }

  static async updateContact (contact: Contact): Promise<AxiosResponse<Contact>> {
    return axios.put(`${ConfigHelper.getAuthAPIUrl()}/users/contacts`, contact)
  }

  static async getOrganizations (): Promise<AxiosResponse<Organizations>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/users/orgs`)
  }

  static async updateUserTerms (identifier: string, termsVersion: string,
    isTermsAccepted: boolean): Promise<AxiosResponse<User>> {
    return axios.patch(`${ConfigHelper.getAuthAPIUrl()}/users/${identifier}`, {
      termsversion: termsVersion,
      istermsaccepted: isTermsAccepted
    }
    )
  }

  static async deactivateUser (): Promise<AxiosResponse<User>> {
    return axios.delete(`${ConfigHelper.getAuthAPIUrl()}/users/@me`)
  }

  static async deleteAnonymousUser (userId: string): Promise<AxiosResponse<User>> {
    return axios.delete(`${ConfigHelper.getAuthAPIUrl()}/users/${encodeURIComponent(userId)}`)
  }

  static async getMembership (orgId: number): Promise<AxiosResponse<Member>> {
    return axios.get(`${ConfigHelper.getAuthAPIUrl()}/users/orgs/${orgId}/membership`)
  }

  static async createUsers (addUsersToOrgBody: AddUsersToOrgBody): Promise<AxiosResponse<BulkUserResponseBody>> {
    return axios.post(`${ConfigHelper.getAuthAPIUrl()}/bulk/users`, addUsersToOrgBody)
  }

  static async resetPassword (username: string, password: string): Promise<AxiosResponse<void>> {
    return axios.patch(`${ConfigHelper.getAuthAPIUrl()}/users/${encodeURIComponent(username)}`, {
      username: username,
      password: password
    }
    )
  }

  static async createUserProfile (token: string, userProfile: UserProfileRequestBody): Promise<AxiosResponse<any>> {
    const headers = {
      'Content-Type': 'application/json',
      'invitation_token': token
    }
    return axios.post(`${ConfigHelper.getAuthAPIUrl()}/users/bcros`, userProfile, {
      headers: headers
    })
  }

  static async resetUser (): Promise<AxiosResponse<any>> {
    return axios.post(`${ConfigHelper.getAuthResetAPIUrl()}`)
  }

  static async createNotaryDetails (documentId: String, notaryInfo: NotaryInformation, notaryContact: NotaryContact, userId: string): Promise<AxiosResponse<User>> {
    const inputrequest = {
      documentId: documentId,
      issuer: notaryInfo.notaryName,
      contact: {
        ...notaryInfo.address,
        email: notaryContact?.email,
        phone: notaryContact?.phone,
        phoneExtension: notaryContact?.extension
      }

    }
    return axios.post(`${ConfigHelper.getAuthAPIUrl()}/users/${encodeURIComponent(userId)}/affidavits`, inputrequest)
  }
}
