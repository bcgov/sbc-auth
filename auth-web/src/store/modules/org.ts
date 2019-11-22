import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import { CreateRequestBody as CreateInvitationRequestBody, Invitation } from '@/models/Invitation'
import { CreateRequestBody as CreateOrgRequestBody, Member, Organization, UpdateMemberPayload } from '@/models/Organization'
import { EmptyResponse } from '@/models/global'
import InvitationService from '@/services/invitation.services'
import OrgService from '@/services/org.services'
import { UserInfo } from '@/models/userInfo'
import UserService from '@/services/user.services'
import _ from 'lodash'

interface SetMemberPayload {
  orgId: number
  member: Member
}

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
  activeOrgMembers: Member[] = []
  pendingOrgMembers: Member[] = []
  pendingOrgInvitations: Invitation[] = []

  // This simply returns the first org in the list.
  // TODO: Once account switching is in place, this will have to return the
  // correct org in the list
  get myOrg (): Organization {
    if (this.organizations && this.organizations.length > 0) {
      return this.organizations[0]
    }
    return undefined
  }

  get myOrgMembership (): Member {
    const currentUser: UserInfo = this.context.rootState.user.currentUser
    if (this.myOrg && currentUser) {
      return this.myOrg.members.find(member => member.user.username === currentUser.userName)
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

  @Action({ rawError: true, commit: 'addOrganization' })
  public async createOrg (createRequestBody: CreateOrgRequestBody) {
    const response = await OrgService.createOrg(createRequestBody)
    if (!response || !response.data) {
      throw new Error('Unknown error has occured while creating the team')
    } else if (response.status === 409) {
      throw new Error('That team already exists')
    } else if (response.status === 201) {
      return response.data
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

  @Action({ rawError: true })
  public async validateInvitationToken (token: string): Promise<EmptyResponse> {
    const response = await InvitationService.validateToken(token)
    return response && response.data ? response.data : undefined
  }

  @Action({ rawError: true })
  public async acceptInvitation (token: string): Promise<Invitation> {
    const response = await InvitationService.acceptInvitation(token)
    return response && response.data ? response.data : undefined
  }

  @Action({ rawError: true })
  public async deleteMember (memberId: number) {
    // Send request to remove member on server and get result
    const response = await OrgService.removeMember(this.context.getters['myOrg'].id, memberId)

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
    const response = await OrgService.updateMember(this.context.getters['myOrg'].id, updatePayload)

    // If no response or error, throw exception to be caught
    if (!response || response.status !== 200 || !response.data) {
      throw Error('Unable to update member role')
    } else {
      this.context.dispatch('syncActiveOrgMembers')
      this.context.dispatch('syncPendingOrgMembers')
    }
  }

  @Action({ commit: 'setOrganizations' })
  public async syncOrganizations () {
    const response = await UserService.getOrganizations()
    return response.data && response.data.orgs ? response.data.orgs : []
  }

  @Action({ commit: 'setActiveOrgMembers', rawError: true })
  public async syncActiveOrgMembers () {
    const response = await OrgService.getOrgMembers(this.context.getters['myOrg'].id, 'ACTIVE')
    return response.data && response.data.members ? response.data.members : []
  }

  @Action({ commit: 'setPendingOrgMembers', rawError: true })
  public async syncPendingOrgMembers () {
    const response = await OrgService.getOrgMembers(this.context.getters['myOrg'].id, 'PENDING_APPROVAL')
    return response.data && response.data.members ? response.data.members : []
  }

  @Action({ commit: 'setPendingOrgInvitations', rawError: true })
  public async syncPendingOrgInvitations () {
    const response = await OrgService.getOrgInvitations(this.context.getters['myOrg'].id, 'PENDING')
    return response.data && response.data.invitations ? response.data.invitations : []
  }
}
