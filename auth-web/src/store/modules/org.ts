import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import { DeleteMemberPayload, Member, Organization, UpdateMemberPayload } from '@/models/Organization'
import { EmptyResponse } from '@/models/global'
import { Invitation, CreateRequestBody } from '@/models/Invitation'
import InvitationService from '@/services/invitation.services'
import OrgService from '@/services/org.services'
import UserService from '@/services/user.services'
import _ from 'lodash'

@Module({
  name: 'org',
  namespaced: true
})
export default class OrgModule extends VuexModule {
  currentOrg: Organization = {
    name: '',
    affiliatedEntities: [],
    members: [],
    invitations: []
  }

  resending = false
  sentInvitations: Invitation[] = []
  failedInvitations: Invitation[] = []
  organizations: Organization[] = []

  @Mutation
  public resetInvitations () {
    this.resending = false
    this.sentInvitations = []
    this.failedInvitations = []
  }

  @Mutation
  public addSentInvitation (sentInvitation: Invitation) {
    this.organizations.forEach(org => {
      if (sentInvitation.membership.some(membership => membership.org.id === org.id)) {
        org.invitations.push(sentInvitation)
      }
    })
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
  public setOrganization (organization: Organization) {
    const index = this.organizations.findIndex(org => org.id === organization.id)
    this.organizations[index] = organization
  }

  @Mutation
  public removeMember (removeMemberPayload: DeleteMemberPayload) {
    const org = this.organizations.find(org => org.id === removeMemberPayload.orgIdentifier)
    const index = org.members.findIndex(member => member.id === removeMemberPayload.memberId)
    org.members.splice(index, 1)
  }

  @Mutation
  public updateMember (updateMemberPayload: UpdateMemberPayload) {
    const org = this.organizations.find(org => org.id === updateMemberPayload.orgIdentifier)
    const member = org.members.find(member => member.id === updateMemberPayload.memberId)
    if (member) {
      member.membershipTypeCode = updateMemberPayload.role
    }
  }

  @Mutation
  public removeInvitation (invitation: Invitation) {
    this.organizations.forEach(org => {
      const index = org.invitations.findIndex(invite => invite.id === invitation.id)
      org.invitations.splice(index, 1)
    })
  }

  @Action({ rawError: true })
  public async createInvitation (invitation: CreateRequestBody) {
    try {
      const response = await InvitationService.createInvitation(invitation)
      if (!response || !response.data || response.status !== 201) {
        throw new Error('Unable to create invitation')
      }
      this.context.commit('addSentInvitation', response.data)
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
  public async deleteInvitation (invitation: Invitation) {
    const prevState = this.context.state
    this.context.commit('removeInvitation', invitation)
    try {
      const response = await InvitationService.deleteInvitation(invitation.id)
      if (!response || response.status !== 200 || !response.data) {
        throw Error('Unable to delete invitation')
      }
    } catch (exception) {
      this.context.state = prevState
    }
  }

  @Action({ rawError: true })
  public async validateInvitationToken (token: string): Promise<EmptyResponse> {
    return InvitationService.validateToken(token).then(response => {
      return response.data
    })
  }

  @Action({ rawError: true })
  public async acceptInvitation (token: string): Promise<Invitation> {
    return InvitationService.acceptInvitation(token).then(response => {
      return response.data
    })
  }

  @Action({ rawError: true })
  public async deleteMember (memberInfo: DeleteMemberPayload) {
    // Update store first (for better UX)
    const prevState = this.context.state
    this.context.commit('removeMember', memberInfo)
    try {
      // Send request to remove member on server and get result
      const response = await OrgService.removeMember(memberInfo.orgIdentifier, memberInfo.memberId)

      // If no response, or error code, throw exception to be caught
      if (!response || response.status !== 200 || !response.data) {
        throw Error('Unable to delete member')
      }
    } catch (exception) {
      // Any errors, roll back to previous state
      this.context.state = prevState
    }
  }

  @Action({ rawError: true })
  public async updateMemberRole (memberInfo: UpdateMemberPayload) {
    // Update store first, but save current role
    // (for UX reasons, we don't make user to wait to see role change)
    const prevState = this.context.state
    this.context.commit('updateMember', memberInfo)
    try {
      // Send request to update member on server and get result
      const response = await OrgService.updateMember(memberInfo.orgIdentifier, memberInfo.memberId, memberInfo.role)

      // If no response or error, throw exception to be caught
      if (!response || response.status !== 200 || !response.data) {
        throw Error('Unable to update member role')
      }
    } catch (exception) {
      // On exception, roll back to previous state
      this.context.state = prevState
    }
  }

  @Action({ commit: 'setOrganizations' })
  public async syncOrganizations () {
    const response = await UserService.getOrganizations()
    return response.data && response.data.orgs ? response.data.orgs : []
  }
}
