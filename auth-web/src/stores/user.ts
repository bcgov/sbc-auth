import { DocumentUpload, User, UserProfileData, UserSettings } from '@/models/user'
import { NotaryContact, NotaryInformation } from '@/models/notary'
import { computed, reactive, toRefs } from '@vue/composition-api'

import CommonUtils from '@/util/common-util'
import { Contact } from '@/models/contact'
import DocumentService from '@/services/document.services'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import KeyCloakService from 'sbc-common-components/src/services/keycloak.services'
import { RoleInfo } from '@/models/Organization'
import { TermsOfUseDocument } from '@/models/TermsOfUseDocument'
import UserService from '@/services/user.services'
import { defineStore } from 'pinia'

export interface UserTerms {
  isTermsOfUseAccepted: boolean
  termsOfUseAcceptedVersion: string
}

export const useUserStore = defineStore('user', () => {
  const state = reactive({
    currentUser: undefined as KCUserProfile,
    userProfile: undefined as User,
    userContact: undefined as Contact,
    termsOfUse: undefined as TermsOfUseDocument,
    userHasToAcceptTOS: false,
    notaryInformation: undefined as NotaryInformation,
    notaryContact: undefined as NotaryContact,
    affidavitDocId: '' as string, // the guid of the doc which you get from the server side
    affidavitDoc: undefined as File,
    userProfileData: undefined as UserProfileData,
    redirectAfterLoginUrl: '' as string,
    roleInfos: undefined as RoleInfo[],
    currentUserAccountSettings: undefined as UserSettings[]
  })

  function $reset () {
    state.currentUser = undefined as KCUserProfile
    state.userProfile = undefined as User
    state.userContact = undefined as Contact
    state.termsOfUse = undefined as TermsOfUseDocument
    state.userHasToAcceptTOS = false
    state.notaryInformation = undefined as NotaryInformation
    state.notaryContact = undefined as NotaryContact
    state.affidavitDocId = '' as string
    state.affidavitDoc = undefined as File
    state.userProfileData = undefined as UserProfileData
    state.redirectAfterLoginUrl = '' as string
    state.roleInfos = undefined as RoleInfo[]
    state.currentUserAccountSettings = undefined as UserSettings[]
  }

  const termsOfUseVersion = computed(() => state.userProfile?.userTerms?.termsOfUseAcceptedVersion)
  const isTermsAccepted = computed(() => state.userProfile?.userTerms?.isTermsOfUseAccepted)

  function setRedirectAfterLoginUrl (url: string) {
    state.redirectAfterLoginUrl = url
  }

  function setAffidavitDoc (affidavitDoc: File) {
    this.affidavitDocId = '' // reset the file id
    this.affidavitDoc = affidavitDoc
  }

  function setNotaryInformation (notaryInformation: NotaryInformation) {
    this.notaryInformation = JSON.parse(JSON.stringify(notaryInformation))
  }

  function setNotaryContact (notaryContact: NotaryContact) {
    state.notaryContact = JSON.parse(JSON.stringify(notaryContact))
  }

  function setUserProfileData (userProfile: UserProfileData | undefined) {
    state.userProfileData = userProfile
  }

  function loadUserInfo () {
    const result = KeyCloakService.getUserInfo()
    state.currentUser = result
    return result
  }

  function reset () {
    state.currentUser = undefined
    state.userProfile = undefined
    state.userContact = undefined
  }

  function setUserProfile (user: User) {
    state.userProfile = user
  }

  async function getUserProfile (identifier: string) {
    const response = await UserService.getUserProfile(identifier)
    if (response?.data) {
      state.userProfile = response.data
      return response.data
    }
  }

  async function getRoleInfo ():Promise<RoleInfo[]> {
    const response = await UserService.getRoles()
    if (response?.data) {
      const result = response.data.sort((a, b) => (a.displayOrder > b.displayOrder) ? 1 : -1)
      state.roleInfos = result
      return result
    }
  }

  async function createAffidavit () {
    // Handle doc Id logic
    const docId = state.affidavitDocId
    const notaryContact = state.notaryContact
    const notaryInfo = state.notaryInformation
    const userId = state.currentUser.keycloakGuid // was from auth/keycloakGuid
    await UserService.createNotaryDetails(docId, notaryInfo, notaryContact, userId)
  }

  async function uploadPendingDocsToStorage () {
    const isPendingUpload = !this.affidavitDocId
    if (isPendingUpload) {
      const file = state.affidavitDoc
      const response = await DocumentService.getPresignedUrl(file.name)
      const doc:DocumentUpload = response?.data
      state.affidavitDocId = doc.key // need this while creating org
      const userId = state.currentUser.keycloakGuid // was from auth/keycloakGuid
      await DocumentService.uploadToUrl(doc.preSignedUrl, file, doc.key, userId)
    }
  }

  async function syncUserProfile () {
    const userResponse = await UserService.getUserProfile('@me')
    if (userResponse?.data) {
      // Refresh token to get the new token with additional roles
      await KeyCloakService.refreshToken(true)
      state.userProfile = userResponse.data
    }

    const contactResponse = await UserService.getContacts()
    if (contactResponse?.data && (contactResponse.status === 200)) {
      let firstContact: Contact
      if (contactResponse.data.contacts.length > 0) {
        firstContact = contactResponse.data.contacts[0]
      }
      state.userContact = firstContact
    }
  }

  async function createUserContact (contact?: Contact) {
    const userProfile = state.userProfileData
    const userContact: Contact = contact || {
      phone: userProfile?.phone,
      email: userProfile?.email,
      phoneExtension: userProfile?.phoneExtension
    }
    const response = await UserService.createContact(userContact)
    if (response?.data && response.status === 201) {
      state.userContact = response.data
      return response.data
    }
  }

  function updateCurrentUserTerms (terms: UserTerms) {
    state.userProfile = { ...state.userProfile, userTerms: terms }
    return terms
  }

  async function updateUserContact (contact?: Contact) {
    const userProfile = state.userProfileData
    const userContact: Contact = contact || {
      phone: userProfile?.phone,
      email: userProfile?.email,
      phoneExtension: userProfile?.phoneExtension
    }
    const response = await UserService.updateContact(userContact)
    if (response?.data && response.status === 200) {
      state.userContact = response.data
      return response.data
    }
  }

  async function updateUserFirstAndLastName (user?: User) {
    const updateUser: any = user || state.userProfileData
    const response = await UserService.updateUserProfile(updateUser.firstname, updateUser.lastname)
    if (response?.data && response.status === 200) {
      state.userProfile = response.data
      return response.data
    }
  }

  async function logout (redirectUrl: string) {
    await KeyCloakService.logout(redirectUrl)
  }

  async function saveUserTerms () {
    const response = await UserService.updateUserTerms('@me', this.termsOfUseVersion, this.isTermsAccepted)
    if (response?.data) {
      return response.data
    }
  }

  async function resetOTPAuthenticator (username: string) {
    const response = await UserService.resetOTPAuthenticator(username)
    return response?.data || {}
  }

  async function getTermsOfUse (docType: string = 'termsofuse') {
    const response = await DocumentService.getTermsOfService(docType)
    const result = response?.data
    state.termsOfUse = result
    const userTOS = state.userProfile?.userTerms?.termsOfUseAcceptedVersion
    if (!userTOS) {
      this.userHasToAcceptTOS = true
    } else {
      const currentlyAcceptedTermsVersion = CommonUtils.extractAndConvertStringToNumber(userTOS)
      const latestVersionNumber = CommonUtils.extractAndConvertStringToNumber(state.termsOfUse?.versionId)
      state.userHasToAcceptTOS = (currentlyAcceptedTermsVersion === latestVersionNumber)
    }
    return result
  }

  async function getUserAccountSettings () {
    const response = await UserService.getUserAccountSettings(this.context.state['userProfile'].keycloakGuid)
    if (response?.data) {
      // filter by account type and sort by name(label)
      const orgs = response.data.filter(userSettings =>
        (userSettings.type === 'ACCOUNT')).sort((a, b) => a.label.localeCompare(b.label))
      state.currentUserAccountSettings = orgs
      return orgs
    }
    state.currentUserAccountSettings = []
    return []
  }

  return {
    createAffidavit,
    createUserContact,
    getRoleInfo,
    getTermsOfUse,
    getUserAccountSettings,
    getUserProfile,
    isTermsAccepted,
    logout,
    loadUserInfo,
    setRedirectAfterLoginUrl,
    setAffidavitDoc,
    setNotaryContact,
    setUserProfileData,
    setNotaryInformation,
    reset,
    resetOTPAuthenticator,
    saveUserTerms,
    setUserProfile,
    syncUserProfile,
    ...toRefs(state),
    termsOfUseVersion,
    updateCurrentUserTerms,
    updateUserContact,
    updateUserFirstAndLastName,
    uploadPendingDocsToStorage,
    $reset
  }
})
