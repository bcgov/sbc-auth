import { Module, VuexModule, Mutation, Action } from 'vuex-module-decorators'
import keycloakService from '@/services/keycloak.services'
import userServices from '@/services/user.services'
import { UserInfo } from '@/models/userInfo'
import { User } from '@/models/user'
import { Contact } from '@/models/contact'
import { Organization, Member, ActiveUserRecord, PendingUserRecord } from '@/models/Organization'
import authService from '@/services/login.services'
import ConfigHelper from '@/util/config-helper'
import OrgService from '@/services/org.services'
import _ from 'lodash'
import { Invitation } from '@/models/Invitation'
import moment from 'moment'

@Module({
  name: 'user',
  namespaced: true
})
export default class UserModule extends VuexModule {
  currentUser: UserInfo
  userProfile: User
  userContact: Contact
  organizations: Organization[] = []
  activeBasicMembers: Member[] = []
  pendingBasicMembers: Invitation[] = []

  get activeUserListing (): ActiveUserRecord[] {
    return this.activeBasicMembers.map(member => {
      return {
        username: member.user.username,
        name: `${member.user.firstname} ${member.user.lastname}`,
        role: member.membershipTypeCode,
        lastActive: moment(member.user.modified).format('DD MMM, YYYY')
      }
    })
  }

  get pendingUserListing (): PendingUserRecord[] {
    return this.pendingBasicMembers.map(invitation => {
      return {
        invitationId: invitation.id,
        email: invitation.recipientEmail,
        invitationSent: moment(invitation.sentDate).format('DD MMM, YYYY'),
        invitationExpires: moment(invitation.expiresOn).format('DD MMM, YYYY')
      }
    })
  }

  @Mutation
  public setOrganizations (organizations: Organization[]) {
    this.organizations = organizations
  }

  @Mutation
  public setUserProfile (userProfile: User) {
    this.userProfile = userProfile
  }

  @Mutation
  public setCurrentUser (currentUser: UserInfo) {
    this.currentUser = currentUser
  }

  @Mutation
  public setUserContact (userContact: Contact) {
    this.userContact = userContact
  }

  @Mutation
  public setActiveBasicMembers (members: Member[]) {
    this.activeBasicMembers = members
  }

  @Mutation
  public setPendingBasicMembers (invitations: Invitation[]) {
    this.pendingBasicMembers = invitations
  }

  @Action({ rawError: true })
  public async initKeycloak (idpHint:string) {
    return keycloakService.init(idpHint)
  }

  @Action({ commit: 'setCurrentUser' })
  public async initializeSession () {
    // Set values to session storage
    keycloakService.initSessionStorage()
    // Load User Info
    return keycloakService.getUserInfo()
  }

  @Action({ commit: 'setUserProfile' })
  public async getUserProfile (identifier: string) {
    return userServices.getUserProfile(identifier)
      .then(response => {
        return response.data ? response.data : null
      })
  }

  @Action({ commit: 'setUserProfile' })
  public async createUserProfile () {
    return userServices.createUserProfile()
      .then(async response => {
        // Refresh token to get the new token with additional roles
        await keycloakService.refreshToken()
        return response.data
      })
  }

  @Action({ commit: 'setUserContact' })
  public async createUserContact (contact:Contact) {
    return userServices.createContact(contact)
      .then(response => {
        return response.data
      })
  }

  @Action({ commit: 'setOrganizations' })
  public async getOrganizations () {
    const response = await userServices.getOrganizations()
    return response.data && response.data.orgs ? response.data.orgs : []
  }

  @Action({ rawError: true })
  public logout (redirectUrl: string) {
    const loginType = ConfigHelper.getFromSession('LOGIN_TYPE')
    const authApiURL = ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API') + '/'
    if (loginType && loginType === 'passcode') {
      authService.logout().then(response => {
        if (response.status === 204) {
          ConfigHelper.clearSession()
          window.location.assign(window.location.origin + '/' + process.env.VUE_APP_PATH)
        }
      })
    } else {
      keycloakService.logout(redirectUrl)
    }
  }

  // This returns a flattened list of users belong to the current users
  // set of implicit orgs (duplicates removed)
  @Action({ commit: 'setActiveBasicMembers' })
  public async getActiveBasicMembers (): Promise<Member[]> {
    let members: Member[] = []
    const orgs = this.context.state['organizations']
    for (let i = 0; i < orgs.length; i++) {
      const organization = orgs[i]
      if (organization.orgType === 'IMPLICIT') {
        const response = await OrgService.getOrgMembers(organization.id)
        if (response.status === 200 && response.data) {
          members = members.concat(response.data.members)
        }
      }
    }
    // Remove duplicates (this is done for IMPLICIT ORGS only since members will have access to entire dashboard)
    members = _.uniqWith(members, (memberA, memberB) => memberA.user.username === memberB.user.username)
    return members
  }

  @Action({ commit: 'setPendingBasicMembers' })
  public async getPendingBasicMembers (): Promise<Invitation[]> {
    let invitations: Invitation[] = []
    const orgs = this.context.state['organizations']
    for (let i = 0; i < orgs.length; i++) {
      const organization = orgs[i]
      if (organization.orgType === 'IMPLICIT') {
        const response = await OrgService.getOrgInvitations(organization.id, 'PENDING')
        if (response.status === 200 && response.data) {
          invitations = invitations.concat(response.data.invitations)
        }
      }
    }
    return invitations
  }
}
