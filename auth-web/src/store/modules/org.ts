import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import { CreateRequestBody, Invitation } from '@/models/Invitation'
import { Member, Organization, UpdateMemberPayload } from '@/models/Organization'
import { Business } from '@/models/business'
import ConfigHelper from '@/util/config-helper'
import { EmptyResponse } from '@/models/global'
import InvitationService from '@/services/invitation.services'
import OrgService from '@/services/org.services'
import { SessionStorageKeys } from '@/util/constants'
import UserService from '@/services/user.services'
import _ from 'lodash'

interface SetMembersPayload {
  orgId: number
  members: Member[]
}

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
  currentOrg: Organization = undefined

  resending = false
  sentInvitations: Invitation[] = []
  failedInvitations: Invitation[] = []
  organizations: Organization[] = []

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
  public setCurrentOrg (org: Organization) {
    ConfigHelper.addToSession(SessionStorageKeys.CurrentOrgId, org.id)
    this.currentOrg = org
  }

  @Mutation
  public setMembers (members: Member[]) {
    if (this.currentOrg) {
      this.currentOrg.members = members
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
    if (this.currentOrg && this.currentOrg.invitations) {
      this.currentOrg.invitations.push(sentInvitation)
    }
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
    if (this.currentOrg && this.currentOrg.members) {
      const index = this.currentOrg.members.findIndex(member => member.id === memberId)
      this.currentOrg.members.splice(index, 1)
    }
  }

  @Mutation
  public updateMember (updateMemberPayload: UpdateMemberPayload) {
    const member = this.currentOrg.members.find(member => member.id === updateMemberPayload.memberId)
    if (member) {
      member.membershipTypeCode = updateMemberPayload.role
    }
  }

  @Mutation
  public removeInvitation (invitationId: number) {
    if (this.currentOrg && this.currentOrg.invitations) {
      const index = this.currentOrg.invitations.findIndex(invitation => invitation.id === invitationId)
      this.currentOrg.invitations.splice(index, 1)
    }
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
  public async deleteInvitation (invitationId: number) {
    const response = await InvitationService.deleteInvitation(invitationId)
    if (!response || response.status !== 200 || !response.data) {
      throw Error('Unable to delete invitation')
    }
    this.context.commit('removeInvitation', invitationId)
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
  public async deleteMember (memberId: number) {
    const currentOrg: Organization = this.context.state['currentOrg']
    const savedMembers = [...currentOrg.members]
    // Update store first (for better UX)
    this.context.commit('removeMember', memberId)
    try {
      // Send request to remove member on server and get result
      const response = await OrgService.removeMember(currentOrg.id, memberId)

      // If no response, or error code, throw exception to be caught
      if (!response || response.status !== 200 || !response.data) {
        throw Error('Unable to delete member')
      }
    } catch (exception) {
      // Any errors, roll back to previous state
      this.context.commit('setMembers', savedMembers)
    }
  }

  @Action({ rawError: true })
  public async updateMemberRole (updatePayload: UpdateMemberPayload) {
    // Update store first, but save current role
    // (for UX reasons, we don't make user to wait to see role change)
    const currentOrg: Organization = this.context.state['currentOrg']
    const targetMember = currentOrg.members.find(member => member.id === updatePayload.memberId)
    const savedRole = targetMember.membershipTypeCode
    this.context.commit('updateMember', updatePayload)
    try {
      // Send request to update member on server and get result
      const response = await OrgService.updateMember(currentOrg.id, targetMember.id, updatePayload.role)

      // If no response or error, throw exception to be caught
      if (!response || response.status !== 200 || !response.data) {
        throw Error('Unable to update member role')
      }
    } catch (exception) {
      // On exception, roll back to previous state
      this.context.commit('updateMember', { ...updatePayload, role: savedRole })
    }
  }

  @Action({ commit: 'setOrganizations' })
  public async syncOrganizations () {
    const response = await UserService.getOrganizations()
    return response.data && response.data.orgs ? response.data.orgs : []
  }

  @Action({ commit: 'setCurrentOrg' })
  public async syncCurrentOrg () {
    const orgId = ConfigHelper.getFromSession(SessionStorageKeys.CurrentOrgId)
    if (orgId) {
      const response = await OrgService.getOrganization(Number.parseInt(ConfigHelper.getFromSession(SessionStorageKeys.CurrentOrgId)))
      return response && response.data ? response.data : undefined
    }
    return undefined
  }
}
