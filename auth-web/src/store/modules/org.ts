import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import { CreateRequestBody as CreateInvitationRequestBody, Invitation } from '@/models/Invitation'
import { CreateRequestBody as CreateOrgRequestBody, Member, Organization, UpdateMemberPayload } from '@/models/Organization'
import { Business } from '@/models/business'
import { EmptyResponse } from '@/models/global'
import InvitationService from '@/services/invitation.services'
import OrgService from '@/services/org.services'
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

  // This simply returns the first org in the list.
  // TODO: Once account switching is in place, this will have to return the
  // correct org in the list
  get myOrg (): Organization {
    if (this.organizations && this.organizations.length > 0) {
      return this.organizations[0]
    }
    return undefined
  }

  get orgMembers () {
    return (orgId: number) => {
      const org = this.organizations.find(org => org.id === orgId)
      if (org) {
        return org.members
      } else {
        return []
      }
    }
  }

  get orgInvitations () {
    return (orgId: number) => {
      const org = this.organizations.find(org => org.id === orgId)
      if (org) {
        return org.invitations
      } else {
        return []
      }
    }
  }

  get orgMember () {
    return (orgId: number, memberId: number) => {
      const org = this.organizations.find(org => org.id === orgId)
      if (org) {
        return org.members.find(member => member.id === memberId)
      } else {
        return null
      }
    }
  }

  get orgAffiliatedBusinesses (): (orgId?: number) => Business[] {
    return (orgId?: number) => {
      if (orgId) {
        const org = this.organizations.find(org => org.id === orgId)
        if (org && org.affiliatedEntities) {
          return org.affiliatedEntities
        }
        return []
      } else {
        // If no orgId provided, return flattened list for all IMPLICIT orgs
        return _.flatten<Business>(this.organizations
          .filter(org => org.orgType === 'IMPLICIT')
          .map(org => org.affiliatedEntities))
      }
    }
  }

  @Mutation
  public addOrganization (org: Organization) {
    this.organizations.push(org)
  }

  @Mutation
  public setMembers (members: Member[]) {
    if (this.myOrg) {
      this.myOrg.members = members
    }
  }

  @Mutation
  public addMember (payload: SetMemberPayload) {
    const org = this.organizations.find(org => org.id === payload.orgId)
    if (org) {
      org.members.push(payload.member)
    }
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
  public setOrganization (organization: Organization) {
    const index = this.organizations.findIndex(org => org.id === organization.id)
    this.organizations[index] = organization
  }

  @Mutation
  public removeMember (memberId: number) {
    if (this.myOrg && this.myOrg.members) {
      const index = this.myOrg.members.findIndex(member => member.id === memberId)
      this.myOrg.members.splice(index, 1)
    }
  }

  @Mutation
  public updateMember (updateMemberPayload: UpdateMemberPayload) {
    const member = this.myOrg.members.find(member => member.id === updateMemberPayload.memberId)
    if (member) {
      member.membershipTypeCode = updateMemberPayload.role
    }
  }

  @Mutation
  public removeInvitation (invitationId: number) {
    debugger
    if (this.myOrg && this.myOrg.invitations) {
      const index = this.myOrg.invitations.findIndex(invitation => invitation.id === invitationId)
      this.myOrg.invitations.splice(index, 1)
    }
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
      this.context.dispatch('syncOrganizations')
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
    this.context.dispatch('syncOrganizations')
  }

  @Action({ rawError: true })
  public async validateInvitationToken (token: string): Promise<EmptyResponse> {
    const response = await InvitationService.validateToken(token)
    if (response && response.data && response.status === 200) {
      return response.data
    }
  }

  @Action({ rawError: true })
  public async acceptInvitation (token: string): Promise<Invitation> {
    const response = await InvitationService.acceptInvitation(token)
    if (response && response.data && response.status === 200) {
      this.context.dispatch('syncOrganizations')
      return response.data
    }
  }

  @Action({ rawError: true })
  public async deleteMember (memberId: number) {
    // Send request to remove member on server and get result
    const response = await OrgService.removeMember(this.context.getters['myOrg'].id, memberId)

    // If no response, or error code, throw exception to be caught
    if (!response || response.status !== 200 || !response.data) {
      throw Error('Unable to delete member')
    } else {
      this.context.dispatch('syncOrganizations')
    }
  }

  @Action({ rawError: true })
  public async updateMemberRole (updatePayload: UpdateMemberPayload) {
    // Send request to update member on server and get result
    const response = await OrgService.updateMember(this.context.getters['myOrg'].id, updatePayload.memberId, updatePayload.role)

    // If no response or error, throw exception to be caught
    if (!response || response.status !== 200 || !response.data) {
      throw Error('Unable to update member role')
    } else {
      this.context.dispatch('syncOrganizations')
    }
  }

  @Action({ commit: 'setOrganizations' })
  public async syncOrganizations () {
    const response = await UserService.getOrganizations()
    return response.data && response.data.orgs ? response.data.orgs : []
  }
}
