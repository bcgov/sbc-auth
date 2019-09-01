import { Module, VuexModule, Mutation, Action } from 'vuex-module-decorators'
import keycloakService from '@/services/keycloak.services'
import userServices from '@/services/user.services'
import { UserInfo } from '@/models/userInfo'
import { User } from '@/models/user'
import { Contact } from '@/models/contact'
import { Organization } from '@/models/Organization'
import AuthService from 'sbc-common-components/src/services/auth.services'
import ConfigHelper from '@/util/config-helper'
import { AppConstants } from '@/util/constants'

@Module({
  name: 'user'
})
export default class UserModule extends VuexModule {
  currentUser: UserInfo

  userProfile: User

  userContact: Contact

  organizations: Organization[] = []

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
      .then(response => {
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
    return userServices.getOrganizations()
      .then(response => {
        return response.data && response.data.orgs ? response.data.orgs : []
      })
  }

  @Action({ rawError: true })
  public logout (redirectUrl: string) {
    const loginType = ConfigHelper.getFromSession('LOGIN_TYPE')
    const authApiURL = ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API') + '/'
    if (loginType && loginType === 'passcode') {
      AuthService.logout(sessionStorage.getItem('KEYCLOAK_REFRESH_TOKEN'), authApiURL).then(response => {
        if (response.status === 204) {
          ConfigHelper.clearSession()
          window.location.assign(window.location.origin + AppConstants.RootPath)
        }
      })
    } else {
      keycloakService.logout(redirectUrl)
    }
  }
}
