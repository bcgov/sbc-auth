import { Module, VuexModule, Mutation, Action } from 'vuex-module-decorators'
import InvitationService from '@/services/invitation.services'
import { Invitation } from '@/models/Invitation'
import { Organization } from '@/models/Organization'

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

  @Action({ rawError: true })
  public createInvitation (invitation: Invitation) {
    try {
      InvitationService.createInvitation(invitation)
      this.context.commit('addSentInvitation', invitation)
    } catch (exception) {
      this.context.commit('addFailedInvitation', invitation)
    }
  }
}
