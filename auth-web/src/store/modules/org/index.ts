import { Module, VuexModule, Mutation, Action } from 'vuex-module-decorators'
import InvitationService from '@/services/invitation.services'
import { Invitation } from '@/models/Invitation'
import { Organization, Member, DeleteMemberPayload } from '@/models/Organization'
import OrgService from '@/services/org.services'
import { EmptyResponse } from '@/models/global'

@Module({
  name: 'org',
  namespaced: true
})
export default class OrgModule extends VuexModule {
  currentOrg: Organization = {
    name: '',
    affiliatedEntities: []
  }

  resending = false
  sentInvitations: Invitation[] = []
  failedInvitations: Invitation[] = []

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

  @Action({ rawError: true })
  public async createInvitation (invitation: Invitation) {
    try {
      await InvitationService.createInvitation(invitation)
      this.context.commit('addSentInvitation', invitation)
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
    await InvitationService.deleteInvitation(invitation.id)
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
    debugger
    return OrgService.removeMember(memberInfo.orgIdentifier, memberInfo.memberId)
  }
}
