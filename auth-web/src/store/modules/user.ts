import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import KeycloakService from '@/services/keycloak.services'
import { User } from '@/models/user'
import { UserInfo } from '@/models/userInfo'
import UserService from '@/services/user.services'

export interface UserTerms {
  isTermsOfUseAccepted: boolean
  termsOfUseAcceptedVersion: string
}

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

  get termsOfUseVersion () {
    return this.userProfile.userTerms.termsOfUseAcceptedVersion
  }

  get isTermsAccepted () {
    return this.userProfile.userTerms.isTermsOfUseAccepted
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

  @Action({ rawError: true })
  public async syncUserProfile () {
    const userResponse = await UserService.syncUserProfile()
    if (userResponse && userResponse.data && (userResponse.status === 200 || userResponse.status === 201)) {
      // Refresh token to get the new token with additional roles
      KeycloakService.refreshToken()
      this.context.commit('setUserProfile', userResponse.data)
    }

    const contactResponse = await UserService.getContacts()
    if (contactResponse && contactResponse.data && (contactResponse.status === 200)) {
      let firstContact: Contact
      if (contactResponse.data.contacts.length > 0) {
        firstContact = contactResponse.data.contacts[0]
      }
      this.context.commit('setUserContact', firstContact)
    }
  }

  @Action({ commit: 'setUserContact' })
  public async createUserContact (contact: Contact) {
    const response = await UserService.createContact(contact)
    if (response && response.data && response.status === 201) {
      return response.data
    }
  }

  @Mutation
  public setCurrentUserTerms (terms: UserTerms) {
    this.userProfile = { ...this.userProfile, userTerms: terms }
  }

  @Action({ commit: 'setCurrentUserTerms' })
  public updateCurrentUserTerms (terms: UserTerms) {
    return terms
  }

  @Action({ commit: 'setUserContact' })
  public async updateUserContact (contact: Contact) {
    const response = await UserService.updateContact(contact)
    if (response && response.data && response.status === 200) {
      return response.data
    }
  }

  @Action({ rawError: true })
  public async logout (redirectUrl: string) {
    await KeycloakService.logout(redirectUrl)
  }

  @Action({})
  public async saveUserTerms () {
    const response = await UserService.updateUserTerms('@me', this.termsOfUseVersion, this.isTermsAccepted)
    if (response && response.data) {
      return response.data
    }
  }
}
