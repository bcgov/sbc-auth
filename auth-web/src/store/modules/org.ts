import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import { AddUsersToOrgBody, BulkUsersFailed, BulkUsersSuccess, CreateRequestBody as CreateOrgRequestBody, Member, Organization, UpdateMemberPayload } from '@/models/Organization'
import { BcolAccountDetails, BcolProfile } from '@/models/bcol'
import { CreateRequestBody as CreateInvitationRequestBody, Invitation } from '@/models/Invitation'
import { Products, ProductsRequestBody } from '@/models/Staff'
import { Account } from '@/util/constants'
import { AccountSettings } from '@/models/account-settings'
import { Address } from '@/models/address'
import BcolService from '@/services/bcol.services'
import { EmptyResponse } from '@/models/global'
import InvitationService from '@/services/invitation.services'
import OrgService from '@/services/org.services'
import StaffService from '@/services/staff.services'
import UserService from '@/services/user.services'

@Module({
  name: 'org',
  namespaced: true
})
export default class OrgModule extends VuexModule {
  list = []
  resending = false
  sentInvitations: Invitation[] = []
  failedInvitations: Invitation[] = []
  currentAccountSettings: AccountSettings = undefined
  currentOrganization: Organization = undefined
  currentMembership: Member = undefined
  activeOrgMembers: Member[] = []
  pendingOrgMembers: Member[] = []
  pendingOrgInvitations: Invitation[] = []
  invalidInvitationToken = false
  tokenError = false
  createdUsers: BulkUsersSuccess[] = []
  failedUsers: BulkUsersFailed[] = []
  selectedAccountType:Account

  @Mutation
  public setGrantAccess (grantAccess: boolean) {
    this.currentOrganization.grantAccess = grantAccess
  }

  @Mutation
  public setSelectedAccountType (selectedAccountType: Account) {
    this.selectedAccountType = selectedAccountType
  }

  @Mutation
  public setActiveOrgMembers (activeMembers: Member[]) {
    this.activeOrgMembers = activeMembers
  }

  @Mutation
  public setPendingOrgMembers (pendingMembers: Member[]) {
    this.pendingOrgMembers = pendingMembers
  }

  @Mutation
  public setPendingOrgInvitations (pendingInvitations: Invitation[]) {
    this.pendingOrgInvitations = pendingInvitations
  }

  @Mutation
  public setCurrentAccountSettings (accountSettings: AccountSettings) {
    this.currentAccountSettings = accountSettings
  }

  @Mutation
  public resetInvitations () {
    this.resending = false
    this.sentInvitations = []
    this.failedInvitations = []
  }

  @Mutation
  public addSentInvitation (sentInvitation: Invitation) {
    this.sentInvitations.push(sentInvitation)
  }

  @Mutation
  public addFailedInvitation (failedInvitation: Invitation) {
    this.failedInvitations.push(failedInvitation)
  }

  @Mutation
  public setResending (resendingStatus: boolean) {
    this.resending = resendingStatus
  }

  @Mutation
  public setCurrentOrganization (organization: Organization | undefined) {
    this.currentOrganization = organization
  }

  @Mutation
  public setCurrentOrganizationAddress (address: Address | undefined) {
    this.currentOrganization.bcolAccountDetails.address = address
  }

  @Mutation
  public setCurrentMembership (membership: Member) {
    this.currentMembership = membership
  }

  @Mutation
  public setCreatedUsers (users: BulkUsersSuccess[]) {
    this.createdUsers = users
  }

  @Mutation
  public setFailedUsers (users: BulkUsersFailed[]) {
    this.failedUsers = users
  }

  @Action({ rawError: true })
  public async resetCurrentOrganization (): Promise<void> {
    this.context.commit('setCurrentOrganization', undefined)
    this.context.commit('setActiveOrgMembers', [])
    this.context.commit('setPendingOrgMembers', [])
    this.context.commit('setPendingOrgInvitations', [])
  }

  @Action({ rawError: true })
  public async syncOrganization (orgId: number): Promise<Organization> {
    const response = await OrgService.getOrganization(orgId)
    const organization = response?.data
    this.context.commit('setCurrentOrganization', organization)
    return organization
  }

  @Action({ rawError: true, commit: 'setCurrentMembership' })
  public async syncMembership (orgId: number): Promise<Member> {
    const response = await UserService.getMembership(orgId)
    return response?.data
  }

  @Action({ rawError: true })
  public async createOrg (createRequestBody: CreateOrgRequestBody): Promise<Organization> {
    const response = await OrgService.createOrg(createRequestBody)
    this.context.commit('setCurrentOrganization', response?.data)
    return response?.data
  }

  @Action({ rawError: true })
  public async validateBcolAccount (bcolProfile: BcolProfile): Promise<BcolAccountDetails> {
    const response = await BcolService.validateBCOL(bcolProfile)
    return response
  }

  @Action({ rawError: true })
  public async updateOrg (createRequestBody: CreateOrgRequestBody) {
    const response = await OrgService.updateOrg(this.context.state['currentOrganization'].id, createRequestBody)
    this.context.commit('setCurrentOrganization', response.data)
    return response?.data
  }

  @Action({ rawError: true })
  public async createInvitation (invitation: CreateInvitationRequestBody) {
    try {
      const response = await InvitationService.createInvitation(invitation)
      if (!response || !response.data || response.status !== 201) {
        throw new Error('Unable to create invitation')
      }
      this.context.commit('addSentInvitation', response.data)
      this.context.dispatch('syncPendingOrgInvitations')
    } catch (exception) {
      this.context.commit('addFailedInvitation', invitation)
      throw exception
    }
  }

  @Action({ rawError: true })
  public async resendInvitation (invitation: Invitation) {
    this.context.commit('resetInvitations')
    this.context.commit('setResending', true)
    try {
      await InvitationService.resendInvitation(invitation)
      this.context.commit('addSentInvitation', invitation)
    } catch (exception) {
      this.context.commit('addFailedInvitation', invitation)
    }
  }

  @Action({ rawError: true })
  public async deleteInvitation (invitationId: number) {
    const response = await InvitationService.deleteInvitation(invitationId)
    if (!response || response.status !== 200 || !response.data) {
      throw Error('Unable to delete invitation')
    }
    this.context.dispatch('syncPendingOrgInvitations')
  }

  @Mutation
  public setInvalidTokenStatus (status:boolean) {
    this.invalidInvitationToken = status
  }

  @Mutation
  public setTokenErrorStatus (status:boolean) {
    this.tokenError = status
  }

  @Action({ rawError: true })
  public async validateInvitationToken (token: string): Promise<EmptyResponse> {
    try {
      const response = await InvitationService.validateToken(token)
      this.context.commit('setInvalidTokenStatus', false)
      this.context.commit('setTokenErrorStatus', false)
      return response && response.data ? response.data : undefined
    } catch (err) {
      if (err.response.status === 400) {
        this.context.commit('setTokenErrorStatus', false)
        this.context.commit('setInvalidTokenStatus', true)
      } else {
        this.context.commit('setTokenErrorStatus', true)
        this.context.commit('setInvalidTokenStatus', false)
      }
    }
  }

  @Action({ rawError: true })
  public async acceptInvitation (token: string): Promise<Invitation> {
    const response = await InvitationService.acceptInvitation(token)
    return response && response.data ? response.data : undefined
  }

  @Action({ rawError: true })
  public async dissolveTeam () {
    // Send request to remove member on server and get result
    const response = await OrgService.deactivateOrg(this.context.state['currentOrganization'].id)

    // If no response, or error code, throw exception to be caught
    if (!response || response.status !== 204) {
      throw Error('Unable to dissolve organisation')
    }
  }

  @Action({ rawError: true })
  public async leaveTeam (memberId: number) {
    // Send request to remove member on server and get result
    const response = await OrgService.leaveOrg(this.context.state['currentOrganization'].id, memberId)

    // If no response, or error code, throw exception to be caught
    if (!response || response.status !== 200 || !response.data) {
      throw Error('Unable to delete member')
    } else {
      this.context.dispatch('syncActiveOrgMembers')
    }
  }

  @Action({ rawError: true })
  public async updateMember (updatePayload: UpdateMemberPayload) {
    // Send request to update member on server and get result
    const response = await OrgService.updateMember(this.context.state['currentOrganization'].id, updatePayload)

    // If no response or error, throw exception to be caught
    if (!response || response.status !== 200 || !response.data) {
      throw Error('Unable to update member role')
    } else {
      this.context.dispatch('syncActiveOrgMembers')
      this.context.dispatch('syncPendingOrgMembers')
    }
  }

  @Action({ rawError: true })
  public async deleteUser (userId: string) {
    // Send request to update member on server and get result
    const response = await UserService.deleteAnonymousUser(userId)

    // If no response or error, throw exception to be caught
    if (!response || response.status !== 204) {
      throw Error('Unable to remove user')
    } else {
      this.context.dispatch('syncActiveOrgMembers')
      this.context.dispatch('syncPendingOrgMembers')
    }
  }

  @Action({ commit: 'setActiveOrgMembers', rawError: true })
  public async syncActiveOrgMembers () {
    const response = await OrgService.getOrgMembers(this.context.state['currentOrganization'].id, 'ACTIVE')
    return response.data && response.data.members ? response.data.members : []
  }

  @Action({ commit: 'setPendingOrgMembers', rawError: true })
  public async syncPendingOrgMembers () {
    const response = await OrgService.getOrgMembers(this.context.state['currentOrganization'].id, 'PENDING_APPROVAL')
    return response.data && response.data.members ? response.data.members : []
  }

  @Action({ commit: 'setPendingOrgInvitations', rawError: true })
  public async syncPendingOrgInvitations () {
    const response = await OrgService.getOrgInvitations(this.context.state['currentOrganization'].id, 'PENDING')
    return response.data && response.data.invitations ? response.data.invitations : []
  }

  @Action({ rawError: true })
  public async addProductsToOrg (productsRequestBody: ProductsRequestBody): Promise<Products> {
    const response = await StaffService.addProducts(this.context.state['currentOrganization'].id, productsRequestBody)
    return response?.data
  }

  @Action({ rawError: true })
  public async createUsers (addUserBody: AddUsersToOrgBody) {
    try {
      const response = await UserService.createUsers(addUserBody)
      if (!response || !response.data || ![200, 201, 207].includes(response.status) || !response.data?.users) {
        throw new Error('Unable to create users')
      } else {
        let users = response.data.users
        let successUsers: BulkUsersSuccess[] = []
        let failedUsers: BulkUsersFailed[] = []
        users.forEach((user) => {
          if (user.http_status === 201) {
            const password = (addUserBody.users.find(({ username }) => username === user.firstname))?.password
            successUsers.push({
              username: user.firstname,
              password: password
            })
          } else {
            failedUsers.push({
              username: user.username,
              error: user.error
            })
          }
        })
        this.context.commit('setCreatedUsers', successUsers)
        this.context.commit('setFailedUsers', failedUsers)
        await this.context.dispatch('syncActiveOrgMembers')
      }
    } catch (exception) {
      throw exception
    }
  }
}
