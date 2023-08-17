import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import { DocumentUpload, User, UserProfileData, UserSettings } from '@/models/user'
import { NotaryContact, NotaryInformation } from '@/models/notary'

import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import DocumentService from '@/services/document.services'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import KeyCloakService from 'sbc-common-components/src/services/keycloak.services'
import { RoleInfo } from '@/models/Organization'
import { SessionStorageKeys } from '@/util/constants'
import { TermsOfUseDocument } from '@/models/TermsOfUseDocument'
import UserService from '@/services/user.services'
import store from '..'

export interface UserTerms {
  isTermsOfUseAccepted: boolean
  termsOfUseAcceptedVersion: string
}

@Module({
  name: 'user',
  namespaced: true,
  store,
  dynamic: true
})
export default class UserModule extends VuexModule {
  currentUser: KCUserProfile = undefined
  userProfile: User = undefined
  userContact: Contact = undefined
  termsOfUse: TermsOfUseDocument = undefined
  userHasToAcceptTOS: boolean = false
  notaryInformation: NotaryInformation = undefined
  notaryContact: NotaryContact = undefined
  affidavitDocId:string = '' // the guid of the doc which you get from the server side
  affidavitDoc:File = undefined
  userProfileData: UserProfileData = undefined

  redirectAfterLoginUrl: string = ''
  roleInfos: RoleInfo[] = undefined
  currentUserAccountSettings: UserSettings[] = undefined

  @Mutation
  public setUserProfile (userProfile: User | undefined) {
    this.userProfile = userProfile
  }

  @Mutation
  public setAffidavitDocId (affidavitDocId: string) {
    this.affidavitDocId = affidavitDocId
  }

  @Mutation
  public setAffidavitDoc (affidavitDoc: File) {
    this.affidavitDocId = '' // reset the file id
    this.affidavitDoc = affidavitDoc
  }

  @Mutation
  public setRoleInfos (roleInfos: RoleInfo[]) {
    this.roleInfos = roleInfos
  }
  @Mutation
  public setNotaryInformation (notaryInformation: NotaryInformation) {
    this.notaryInformation = JSON.parse(JSON.stringify(notaryInformation))
  }
  @Mutation
  public setNotaryContact (notaryContact: NotaryContact) {
    this.notaryContact = JSON.parse(JSON.stringify(notaryContact))
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

  @Mutation
  public setTermsOfUse (termsOfUse: TermsOfUseDocument) {
    this.termsOfUse = termsOfUse
    const userTOS = this.userProfile?.userTerms?.termsOfUseAcceptedVersion
    if (!userTOS) {
      this.userHasToAcceptTOS = true
    } else {
      const currentlyAcceptedTermsVersion = CommonUtils.extractAndConvertStringToNumber(userTOS)
      const latestVersionNumber = CommonUtils.extractAndConvertStringToNumber(termsOfUse?.versionId)
      this.userHasToAcceptTOS = (currentlyAcceptedTermsVersion === latestVersionNumber)
    }
  }

  @Mutation
  public setUserProfileData (userProfile: UserProfileData | undefined) {
    this.userProfileData = userProfile
  }

  @Mutation
  public setCurrentUserAccountSettings (currentUserAccountSettings: UserSettings[]) {
    this.currentUserAccountSettings = currentUserAccountSettings
  }

  @Action({ commit: 'setCurrentUser' })
  public loadUserInfo () {
    // Load User Info
    return KeyCloakService.getUserInfo()
  }

  @Action({ rawError: true })
  public async reset () {
    this.context.commit('setCurrentUser', undefined)
    this.context.commit('setUserProfile', undefined)
    this.context.commit('setUserContact', undefined)
  }

  @Action({ commit: 'setUserProfile' })
  public async getUserProfile (identifier: string) {
    const response = await UserService.getUserProfile(identifier)
    if (response && response.data) {
      return response.data
    }
  }

  @Action({ commit: 'setRoleInfos' })
  public async getRoleInfo ():Promise<RoleInfo[]> {
    const response = await UserService.getRoles()
    if (response && response.data) {
      return response.data.sort((a, b) => (a.displayOrder > b.displayOrder) ? 1 : -1)
    }
  }

  @Action({ rawError: true })
  public async createAffidavit () {
    // Handle doc Id logic
    const docId = this.context.state['affidavitDocId']
    const notaryContact = this.context.state['notaryContact']
    const notaryInfo = this.context.state['notaryInformation']
    const userId = this.context.rootGetters['auth/keycloakGuid']
    // TODO handle error cases
    await UserService.createNotaryDetails(docId, notaryInfo, notaryContact, userId)
  }

  @Action({ rawError: true })
  public async uploadPendingDocsToStorage () {
    const isPendingUpload = !this.affidavitDocId
    if (isPendingUpload) {
      const file = this.context.state['affidavitDoc']
      const response = await DocumentService.getPresignedUrl(file.name)
      const doc:DocumentUpload = response?.data
      this.context.commit('setAffidavitDocId', doc.key) // need this while creating org
      const userId = this.context.rootGetters['auth/keycloakGuid']
      const res = await DocumentService.uplpoadToUrl(doc.preSignedUrl, file, doc.key, userId)
    }
  }

  @Action({ rawError: true })
  public async syncUserProfile () {
    const userResponse = await UserService.getUserProfile('@me')
    if (userResponse && userResponse.data) {
      // Refresh token to get the new token with additional roles
      await KeyCloakService.refreshToken(true)
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
  public async createUserContact (contact?: Contact) {
    const userProfile = this.context.state['userProfileData']
    const userContact: Contact = contact || {
      phone: userProfile?.phone,
      email: userProfile?.email,
      phoneExtension: userProfile?.phoneExtension
    }
    const response = await UserService.createContact(userContact)
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
  public async updateUserContact (contact?: Contact) {
    const userProfile = this.context.state['userProfileData']
    const userContact: Contact = contact || {
      phone: userProfile?.phone,
      email: userProfile?.email,
      phoneExtension: userProfile?.phoneExtension
    }
    const response = await UserService.updateContact(userContact)
    if (response && response.data && response.status === 200) {
      return response.data
    }
  }

  @Action({ commit: 'setUserProfile' })
  public async updateUserFirstAndLastName (user?: User) {
    const updateUser: any = user || this.context.state['userProfileData']
    const response = await UserService.updateUserProfile(updateUser.firstname, updateUser.lastname)
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

  @Action({ rawError: true })
  public async resetOTPAuthenticator (username: string) {
    const response = await UserService.resetOTPAuthenticator(username)
    return response?.data || {}
  }

  @Action({ commit: 'setTermsOfUse', rawError: true })
  public async getTermsOfUse (docType: string = 'termsofuse') {
    const response = await DocumentService.getTermsOfService(docType)
    return response?.data
  }

  @Action({ commit: 'setCurrentUserAccountSettings', rawError: true })
  public async getUserAccountSettings () {
    const response = await UserService.getUserAccountSettings(this.context.state['userProfile'].keycloakGuid)
    if (response && response.data) {
      // filter by account type and sort by name(label)
      const orgs = response.data.filter(userSettings => (userSettings.type === 'ACCOUNT')).sort((a, b) => a.label.localeCompare(b.label))
      return orgs
    }
    return []
  }
}
