import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import KeyCloakService from 'sbc-common-components/src/services/keycloak.services'
import { TermsOfUseDocument } from '@/models/TermsOfUseDocument'
import { User } from '@/models/user'
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
  currentUser: KCUserProfile = undefined
  userProfile: User = undefined
  userContact: Contact = undefined
  termsOfUse: TermsOfUseDocument = undefined
  redirectAfterLoginUrl: string = ''

  @Mutation
  public setUserProfile (userProfile: User) {
    this.userProfile = userProfile
  }

  @Mutation
  public setRedirectAfterLoginUrl (url: string) {
    this.redirectAfterLoginUrl = url
  }

  get termsOfUseVersion () {
    return this.userProfile?.userTerms?.termsOfUseAcceptedVersion
  }

  get isTermsAccepted () {
    return this.userProfile?.userTerms?.isTermsOfUseAccepted
  }

  @Mutation
  public setCurrentUser (currentUser: KCUserProfile) {
    this.currentUser = currentUser
  }

  @Mutation
  public setUserContact (userContact: Contact) {
    this.userContact = userContact
  }

  @Action({ commit: 'setCurrentUser' })
  public loadUserInfo () {
    // Load User Info
    return KeyCloakService.getUserInfo()
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
      KeyCloakService.refreshToken()
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
    await KeyCloakService.logout(redirectUrl)
  }

  @Action({})
  public async saveUserTerms () {
    const response = await UserService.updateUserTerms('@me', this.termsOfUseVersion, this.isTermsAccepted)
    if (response && response.data) {
      return response.data
    }
  }

  @Mutation
  public setTermsOfUse (termsOfUse: TermsOfUseDocument) {
    this.termsOfUse = termsOfUse
  }
}
