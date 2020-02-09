import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import { CreateRequestBody as CreateInvitationRequestBody, Invitation } from '@/models/Invitation'
import { CreateRequestBody as CreateOrgRequestBody, Member, MembershipStatus, MembershipType, Organization, UpdateMemberPayload } from '@/models/Organization'
import ConfigHelper from '@/util/config-helper'
import { EmptyResponse } from '@/models/global'
import InvitationService from '@/services/invitation.services'
import OrgService from '@/services/org.services'
import { SessionStorageKeys } from '@/util/constants'
import { UserInfo } from '@/models/userInfo'
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
  organizations: Organization[] = []
  currentOrganization: Organization = undefined
  activeOrgMembers: Member[] = []
  pendingOrgMembers: Member[] = []
  pendingOrgInvitations: Invitation[] = []
  orgCreateMessage = 'success'
  invalidInvitationToken = false
  tokenError = false

  get myOrgMembership (): Member {
    const currentUser: UserInfo = this.context.rootState.user.currentUser
    const orgMembers: Member[] = [...this.context.rootState.org.activeOrgMembers, ...this.context.rootState.org.pendingOrgMembers]
    if (orgMembers && currentUser) {
      return orgMembers.find(member => member.user.username === currentUser.userName)
    }
    return undefined
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
  public addOrganization (org: Organization) {
    this.organizations.push(org)
  }

  @Mutation
  public updateOrganization (org: Organization) {
    ConfigHelper.addToSession(SessionStorageKeys.AccountName, org.name)
    const index = this.organizations.findIndex(item => item.id === org.id)
    this.organizations.splice(index, 1, org)
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
  public setOrganizations (organizations: Organization[]) {
    this.organizations = organizations
  }

  @Mutation
  public setOrgCreateMessage (message: string) {
    this.orgCreateMessage = message
  }

  @Mutation
  public setCurrentOrganization (organization: Organization) {
    this.currentOrganization = organization
  }

  @Action({ rawError: true })
  public async syncCurrentOrganization (organization: Organization): Promise<void> {
    this.context.commit('setCurrentOrganization', organization)
    await this.context.dispatch('syncActiveOrgMembers')
    await this.context.dispatch('syncPendingOrgMembers')
    await this.context.dispatch('syncPendingOrgInvitations')
    ConfigHelper.addToSession(SessionStorageKeys.AccountName, organization.name)
  }

  @Action({ rawError: true })
  public async createOrg (createRequestBody: CreateOrgRequestBody) {
    try {
      const response = await OrgService.createOrg(createRequestBody)
      this.context.commit('setOrgCreateMessage', 'success')
      this.context.commit('addOrganization', response.data)
    } catch (err) {
      switch (err.response.status) {
        case 409:
          this.context.commit('setOrgCreateMessage', 'An account with this name already exists. Try a different account name.')
          break
        case 400:
          this.context.commit('setOrgCreateMessage', 'Invalid account name')
          break
        default:
          this.context.commit('setOrgCreateMessage', 'An error occurred while attempting to create your account.')
          break
      }
    }
  }

  @Action({ rawError: true })
  public async updateOrg (createRequestBody: CreateOrgRequestBody) {
    try {
      const response = await OrgService.updateOrg(this.context.state['currentOrganization'].id, createRequestBody)
      this.context.commit('setOrgCreateMessage', 'success')
      this.context.commit('updateOrganization', response.data)
      this.context.commit('setCurrentOrganization', response.data)
    } catch (err) {
      switch (err.response.status) {
        case 409:
          this.context.commit('setOrgCreateMessage', 'An account with this name already exists.')
          break
        case 400:
          this.context.commit('setOrgCreateMessage', 'Invalid account name')
          break
        default:
          this.context.commit('setOrgCreateMessage', 'An error occurred while updating your account name.')
          break
      }
    }
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
  public async syncOrganizations () {
    const response = await UserService.getOrganizations()
    if (response && response.data && response.status === 200) {
      this.context.commit('setOrganizations', response.data.orgs)
      if (response.data.orgs && response.data.orgs.length > 0) {
        await this.context.dispatch('syncCurrentOrganization', response.data.orgs[0])
      }
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
}
