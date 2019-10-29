import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import KeycloakService from '@/services/keycloak.services'
import LoginService from '@/services/login.services'
import { User } from '@/models/user'
import { UserInfo } from '@/models/userInfo'
import UserService from '@/services/user.services'

@Module({
  name: 'user',
  namespaced: true
})
export default class UserModule extends VuexModule {
  currentUser: UserInfo = undefined
  userProfile: User = undefined
  userContact: Contact = undefined

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
    return KeycloakService.init(idpHint)
  }

  @Action({ commit: 'setCurrentUser' })
  public initializeSession () {
    // Set values to session storage
    KeycloakService.initSession()
    // Load User Info
    return KeycloakService.getUserInfo()
  }

  @Action({ commit: 'setUserProfile' })
  public async getUserProfile (identifier: string) {
    const response = await UserService.getUserProfile(identifier)
    if (response && response.data) {
      return response.data
    }
  }

  @Action({ commit: 'setUserProfile' })
  public async createUserProfile () {
    return UserService.createUserProfile()
      .then(async response => {
        // Refresh token to get the new token with additional roles
        KeycloakService.refreshToken()
        return response.data
      })
  }

  @Action({ commit: 'setUserContact' })
  public async createUserContact (contact: Contact) {
    const response = await UserService.createContact(contact)
    if (response && response.data && response.status === 201) {
      return response.data
    }
  }

  @Action({ commit: 'setUserContact' })
  public async updateUserContact (contact: Contact) {
    const response = await UserService.updateContact(contact)
    if (response && response.data && response.status === 200) {
      return response.data
    }
  }

  @Action({ rawError: true })
  public logout (redirectUrl: string) {
    const loginType = ConfigHelper.getFromSession('LOGIN_TYPE')
    const authApiURL = ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API') + '/'
    if (loginType && loginType === 'passcode') {
      LoginService.logout().then(response => {
        if (response.status === 204) {
          ConfigHelper.clearSession()
          window.location.assign(window.location.origin + '/' + process.env.VUE_APP_PATH)
        }
      })
    } else {
      KeycloakService.logout(redirectUrl)
    }
  }
}
