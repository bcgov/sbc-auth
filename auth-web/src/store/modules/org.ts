import {
  AccessType,
  Account,
  AccountStatus,
  FeeCodes,
  PatchActions,
  PaymentTypes,
  Permission,
  ProductStatus,
  Role,
  SessionStorageKeys
} from '@/util/constants'
import {
  AccountFee,
  AddUserBody,
  AddUsersToOrgBody,
  BulkUsersFailed,
  BulkUsersSuccess,
  CreateRequestBody as CreateOrgRequestBody,
  CreateRequestBody,
  GLInfo,
  Member,
  MembershipStatus,
  MembershipType,
  OrgBusinessType,
  OrgPaymentDetails,
  OrgProduct,
  OrgProductFeeCode,
  OrgProductsRequestBody,
  Organization,
  PADInfo,
  PADInfoValidation,
  PatchOrgPayload,
  UpdateMemberPayload
} from '@/models/Organization'
import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import { BcolAccountDetails, BcolProfile } from '@/models/bcol'
import { CreateRequestBody as CreateInvitationRequestBody, Invitation } from '@/models/Invitation'
import { Products, ProductsRequestBody } from '@/models/Staff'
import { StatementFilterParams, StatementListItem, StatementNotificationSettings, StatementSettings } from '@/models/statement'
import { TransactionFilter, TransactionFilterParams, TransactionTableList, TransactionTableRow } from '@/models/transaction'

import { AccountSettings } from '@/models/account-settings'
import { Address } from '@/models/address'
import { AutoCompleteResponse } from '@/models/AutoComplete'
import BcolService from '@/services/bcol.services'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { EmptyResponse } from '@/models/global'
import InvitationService from '@/services/invitation.services'
import { InvoiceList } from '@/models/invoice'
import KeyCloakService from 'sbc-common-components/src/services/keycloak.services'
import OrgService from '@/services/org.services'
import PaymentService from '@/services/payment.services'
import PermissionService from '@/services/permission.services'
import StaffService from '@/services/staff.services'
import UserService from '@/services/user.services'
import { UserSettings } from 'sbc-common-components/src/models/userSettings'
import VonService from '@/services/von.services'

@Module({
  name: 'org',
  namespaced: true
})
export default class OrgModule extends VuexModule {
  list = []
  resending = false
  sentInvitations: Invitation[] = []
  failedInvitations: Invitation[] = []
  currentAccountSettings: AccountSettings = undefined
  currentOrganization: Organization = undefined
  currentOrgAddress:Address = undefined
  currentOrgPaymentType: string = undefined
  currentOrgPADInfo: PADInfo = undefined
  currentOrganizationType: string = undefined
  currentMembership: Member = undefined
  activeOrgMembers: Member[] = []
  pendingOrgMembers: Member[] = []
  pendingOrgInvitations: Invitation[] = []
  invalidInvitationToken = false
  tokenError = false
  createdUsers: BulkUsersSuccess[] = []
  failedUsers: BulkUsersFailed[] = []
  permissions: string[] = []
  accessType: string
  memberLoginOption = ''
  currentOrgGLInfo: GLInfo = undefined
  productList: OrgProduct[] = [] // list of all products
  currentSelectedProducts:any = [] // selected product list code in array

  currentStatementNotificationSettings: StatementNotificationSettings = {} as StatementNotificationSettings
  currentOrgTransactionList: TransactionTableRow[] = []
  statementSettings: StatementSettings = {} as StatementSettings
  orgProductFeeCodes: OrgProductFeeCode[] = []
  currentAccountFees: AccountFee[] = []
  currentOrgPaymentDetails:OrgPaymentDetails[] = []
  isCurrentSelectedProductsPremiumOnly = false
  resetAccountTypeOnSetupAccount = false // this flag use to check need to reset accounttype select when moving back and forth in stepper
  vDisplayModeValue = ''// DisplayModeValues.VIEW_ONLY

  /** Is True if the current account is premium. */
  get isPremiumAccount (): boolean {
    return this.currentOrganization?.orgType === Account.PREMIUM
  }

  get needMissingBusinessDetailsRedirect (): boolean {
    return typeof (this.currentOrganization?.isBusinessAccount) === 'undefined' && this.currentOrganization?.accessType !== AccessType.GOVM && this.canEditBusinessInfo
  }

  private get canEditBusinessInfo (): boolean {
    return [Permission.EDIT_BUSINESS_INFO].some(per => this.permissions.includes(per))
  }

  @Mutation
  public setIsCurrentSelectedProductsPremiumOnly (isCurrentSelectedProductsPremiumOnly:boolean) {
    this.isCurrentSelectedProductsPremiumOnly = isCurrentSelectedProductsPremiumOnly
  }

  @Mutation
  public setAccessType (accessType:string) {
    this.accessType = accessType
  }

  @Mutation
  public setMemberLoginOption (memberLoginOption:string) {
    this.memberLoginOption = memberLoginOption
  }

  @Mutation
  public setGrantAccess (grantAccess: boolean) {
    if (this.currentOrganization) {
      this.currentOrganization = { ...this.currentOrganization, grantAccess }
    }
  }

  @Mutation
  public resetCurrentOrganisation () {
    this.currentOrganization = { name: '' }
  }

  @Mutation
  public resetBcolDetails () {
    this.currentOrganization.bcolProfile = undefined
    this.currentOrganization.bcolAccountDetails = undefined
    this.currentOrgAddress = undefined
  }

  @Mutation
  public setSelectedAccountType (selectedAccountType: Account | undefined) {
    if (this.currentOrganization) {
      this.currentOrganization.orgType = selectedAccountType
    }
  }

  @Mutation
  public setActiveOrgMembers (activeMembers: Member[]) {
    this.activeOrgMembers = activeMembers
  }

  @Mutation
  public setPendingOrgMembers (pendingMembers: Member[]) {
    this.pendingOrgMembers = pendingMembers
  }

  @Mutation
  public setPendingOrgInvitations (pendingInvitations: Invitation[]) {
    this.pendingOrgInvitations = pendingInvitations
  }

  @Mutation
  public setCurrentAccountSettings (accountSettings: AccountSettings) {
    this.currentAccountSettings = accountSettings
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
  public setCurrentOrganization (organization: Organization | undefined) {
    this.currentOrganization = organization
    // for keeping a constant format for BCOL account banner
    if (organization?.bcolAccountId && organization?.bcolUserId) {
      this.currentOrganization.bcolAccountDetails = {
        accountNumber: organization.bcolAccountId,
        userId: organization.bcolUserId
      }
    }
  }

  @Mutation
  public setCurrentMembership (membership: Member) {
    this.currentMembership = membership
  }

  @Mutation
  public setPermissions (permissions: string[]) {
    this.permissions = permissions
  }

  @Mutation
  public setCreatedUsers (users: BulkUsersSuccess[]) {
    this.createdUsers = users
  }

  @Mutation
  public setFailedUsers (users: BulkUsersFailed[]) {
    this.failedUsers = users
  }

  @Mutation
  public setCurrentOrgTransactionList (transactionResp: TransactionTableList) {
    this.currentOrgTransactionList = transactionResp.transactionsList
  }

  @Mutation
  public setStatementSettings (statementSettings: StatementSettings) {
    this.statementSettings = statementSettings
  }

  @Mutation
  public setStatementNotificationSettings (settings: StatementNotificationSettings) {
    this.currentStatementNotificationSettings = settings
  }

  @Mutation
  public setCurrentOrganizationAddress (address: Address | undefined) {
    this.currentOrgAddress = (address) ? JSON.parse(JSON.stringify(address)) : undefined
  }

  @Mutation
  public setCurrentOrganizationName (name: string) {
    this.currentOrganization.name = name
  }

  @Mutation
  public setCurrentOrganizationPaymentType (paymentType: string) {
    this.currentOrgPaymentType = paymentType
  }

  @Mutation
  public setCurrentOrganizationPaymentDetails (orgPaymentDetails: OrgPaymentDetails[]) {
    this.currentOrgPaymentDetails = orgPaymentDetails
  }

  @Mutation
  public setCurrentOrganizationType (orgType: string) {
    this.currentOrganizationType = orgType
  }

  @Mutation
  public setCurrentOrganizationPADInfo (padInfo: PADInfo) {
    this.currentOrgPADInfo = padInfo
  }

  @Mutation
  public setCurrentOrganizationGLInfo (glInfo: GLInfo) {
    this.currentOrgGLInfo = glInfo
  }
  @Mutation
  public setProductList (products: OrgProduct[]) {
    this.productList = products
  }

  @Mutation
  public setCurrentSelectedProducts (productCodeList: []) {
    this.currentSelectedProducts = productCodeList
  }

  @Mutation
  public setOrgProductFeeCodes (orgProductFeeCodes: OrgProductFeeCode[]) {
    this.orgProductFeeCodes = orgProductFeeCodes
  }

  @Mutation
  public setCurrentAccountFees (accountFee: AccountFee[]) {
    this.currentAccountFees = accountFee
  }

  @Mutation
  public resetCurrentAccountFees () {
    this.currentAccountFees = []
  }

  @Mutation
  public setResetAccountTypeOnSetupAccount (resetAccountTypeOnSetupAccount:boolean) {
    this.resetAccountTypeOnSetupAccount = resetAccountTypeOnSetupAccount
  }
  @Mutation
  public setViewOnlyMode (viewOnlyModeValue:string) {
    this.vDisplayModeValue = viewOnlyModeValue
  }

  @Mutation
  public setCurrentOrganizationBusinessType (orgBusinessType: OrgBusinessType) {
    this.currentOrganization = { ...this.currentOrganization, ...orgBusinessType }
  }

  @Mutation
  public resetCurrentSelectedProducts () {
    this.currentSelectedProducts = []
  }

  get isBusinessAccount (): boolean {
    return this.currentOrganization?.isBusinessAccount === true
  }

  @Action({ rawError: true })
  public async resetCurrentOrganization (): Promise<void> {
    this.context.commit('setCurrentOrganization', undefined)
    this.context.commit('setActiveOrgMembers', [])
    this.context.commit('setPendingOrgMembers', [])
    this.context.commit('setPendingOrgInvitations', [])
  }

  @Action({ rawError: true })
  public async syncOrganization (orgId: number): Promise<Organization> {
    const response = await OrgService.getOrganization(orgId)
    const organization = response?.data
    this.context.commit('setCurrentOrganization', organization)
    return organization
  }

  @Action({ rawError: true })
  public async suspendOrganization (suspensionReasonCode: string) {
    const orgId = this.context.state['currentOrganization']?.id
    const orgStatus = this.context.state['currentOrganization'].statusCode === AccountStatus.ACTIVE ? AccountStatus.SUSPENDED : AccountStatus.ACTIVE
    if (orgId && orgStatus) {
      try {
        const patchOrgPayload: PatchOrgPayload = {
          action: PatchActions.UPDATE_STATUS,
          statusCode: orgStatus,
          suspensionReasonCode: suspensionReasonCode
        }
        const response = await OrgService.patchOrg(orgId, patchOrgPayload)
        if (response.status === 200) {
          await this.context.dispatch('syncOrganization', orgId)
        }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Suspend/Unsuspend Account operation failed! - ', error)
      }
    }
  }

  @Action({ rawError: true })
  public async syncMemberLoginOption (orgId: number): Promise<string> {
    const response = await OrgService.getMemberLoginOption(orgId)
    this.context.commit('setMemberLoginOption', response)
    return response
  }

  @Action({ rawError: true })
  public async syncMembership (orgId: number): Promise<Member> {
    let permissions:string[] = []
    let response
    let membership:Member = null
    const kcUserProfile = KeyCloakService.getUserInfo()
    if (!kcUserProfile.roles.includes(Role.Staff)) {
      response = await UserService.getMembership(orgId)
      membership = response?.data
      // const org: Organization = this.context.state['currentOrganization']
      const currentAccountSettings = this.context.state['currentAccountSettings']
      // const statusCode = org && org.statusCode ? org?.statusCode : currentAccountSettings.accountStatus
      const statusCode = currentAccountSettings.accountStatus
      // to fix permission issue. take status from currentAccountSettings
      const res = await PermissionService.getPermissions(statusCode, membership?.membershipTypeCode)
      permissions = res?.data
    } else {
      // Check for better approach
      // Create permissions to enable actions for staff
      if (kcUserProfile.roles.includes(Role.StaffManageAccounts)) {
        permissions = CommonUtils.getAdminPermissions()
      } else if (kcUserProfile.roles.includes(Role.StaffViewAccounts)) {
        permissions = CommonUtils.getViewOnlyPermissions()
      }
      // Create an empty membership model for staff. Map view_account as User and manage_accounts as Admin
      let membershipTypeCode = null
      if (kcUserProfile.roles.includes(Role.StaffManageAccounts)) {
        membershipTypeCode = MembershipType.Admin
      } else if (kcUserProfile.roles.includes(Role.StaffViewAccounts)) {
        membershipTypeCode = MembershipType.User
      }

      membership = {
        membershipTypeCode: membershipTypeCode,
        id: null,
        membershipStatus: MembershipStatus.Active,
        user: null
      }
    }
    permissions = permissions || []
    this.context.commit('setCurrentMembership', membership)
    this.context.commit('setPermissions', permissions)
    return response?.data
  }

  /*
   * staff doesnt need any other store set up's since he doesnt belong to an account
   * So a minimal method to create org
   */
  @Action({ rawError: true })
  public async createOrgByStaff (createRequestBody: CreateOrgRequestBody): Promise<Organization> {
    const response = await OrgService.createOrg(createRequestBody)
    this.context.commit('setCurrentOrganization', response?.data)
    return response?.data
  }

  @Action({ rawError: true })
  public async updateLoginOption (loginOption: string): Promise<string> {
    const org:Organization = this.context.state['currentOrganization']
    const newLoginOption = await OrgService.updateMemberLoginOption(org.id, loginOption)
    this.context.commit('setMemberLoginOption', loginOption)
    return newLoginOption
  }

  @Action({ rawError: true })
  public async createOrg (): Promise<Organization> {
    const org: Organization = this.context.state['currentOrganization']
    const address = this.context.state['currentOrgAddress']
    const paymentMethod = this.context.state['currentOrgPaymentType']
    const padInfo: PADInfo = this.context.state['currentOrgPADInfo']

    const currentSelectedProducts = this.context.state['currentSelectedProducts']
    // setting product subscriptions in required format
    const productsSelected: [] = currentSelectedProducts.map((code) => {
      return {
        productCode: code
      }
    })

    const createRequestBody: CreateRequestBody = {
      name: org.name,
      accessType: this.context.state['accessType'],
      typeCode: org.orgType,
      productSubscriptions: productsSelected,
      isBusinessAccount: org.isBusinessAccount
    }
    if (org.bcolProfile) {
      createRequestBody.bcOnlineCredential = org.bcolProfile
    }
    if (address) {
      createRequestBody.mailingAddress = address
    }
    if (paymentMethod) {
      createRequestBody.paymentInfo = {
        paymentMethod: (paymentMethod === PaymentTypes.CREDIT_CARD) ? PaymentTypes.DIRECT_PAY : paymentMethod
      }
    }
    if (padInfo && createRequestBody.paymentInfo) {
      createRequestBody.paymentInfo.bankTransitNumber = padInfo.bankTransitNumber
      createRequestBody.paymentInfo.bankInstitutionNumber = padInfo.bankInstitutionNumber
      createRequestBody.paymentInfo.bankAccountNumber = padInfo.bankAccountNumber
    }
    if (org.isBusinessAccount) {
      createRequestBody.businessSize = org.businessSize
      createRequestBody.businessType = org.businessType
      createRequestBody.branchName = org.branchName
    }
    const response = await OrgService.createOrg(createRequestBody)
    const organization = response?.data
    this.context.commit('setCurrentOrganization', organization)
    this.context.dispatch('resetoCurrentSelectedProducts') // resting selected product list after account create
    await this.addOrgSettings(organization)
    return response?.data
  }

  @Action({ rawError: true })
  public async createGovmOrg (): Promise<Organization> {
    const org: Organization = this.context.state['currentOrganization']
    const address = this.context.state['currentOrgAddress']
    const revenueAccount: GLInfo = this.context.state['currentOrgGLInfo']
    const currentSelectedProducts = this.context.state['currentSelectedProducts']
    // setting product subscriptions in requiered format
    const productsSelected: [] = currentSelectedProducts.map((code) => {
      return {
        productCode: code
      }
    })

    // we dont need org name and branch name as we are updating the already created org(when staff sends invite)
    const createRequestBody: CreateRequestBody = {
      paymentInfo: {
        revenueAccount,
        paymentMethod: PaymentTypes.EJV
      },
      productSubscriptions: productsSelected
    }

    if (address) {
      createRequestBody.mailingAddress = address
    }

    // need to get org id from state
    const response = await OrgService.updateOrg(org.id, createRequestBody)
    const organization = response?.data
    this.context.commit('setCurrentOrganization', organization)
    await this.addOrgSettings(organization)
    return response?.data
  }

  @Action({ rawError: true })
  public async validatePADInfo (): Promise<PADInfoValidation> {
    const padInfo: PADInfo = { ...this.context.state['currentOrgPADInfo'] }
    delete padInfo.isTOSAccepted
    try {
      const response = await PaymentService.verifyPADInfo(padInfo)
      const verifyPad: PADInfoValidation = response?.data
      // is validation service not reachable ,ignore and proceed
      if (verifyPad?.statusCode !== 200) {
        return { isValid: true } as PADInfoValidation
      }
      return response?.data
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('PAD Verification API Failed! - ', error)
      return {
        isValid: true, // IMPORTANT: True - since we need to create the account even if this api fails.
        statusCode: error?.response?.status || 500,
        message: error?.response?.message || 'Failed'
      }
    }
  }

  @Action({ rawError: true })
  public async addOrgSettings (org: Organization): Promise<UserSettings> {
    const accountSettings: UserSettings = {
      id: org?.id.toString(),
      label: org?.name,
      type: 'ACCOUNT',
      urlorigin: '',
      urlpath: `/account/${org?.id}/settings`,
      accountType: org?.orgType,
      accountStatus: org?.accountStatus
    }
    ConfigHelper.addToSession(SessionStorageKeys.CurrentAccount, JSON.stringify(accountSettings))
    return accountSettings
  }

  @Action({ rawError: true })
  public async validateBcolAccount (bcolProfile: BcolProfile): Promise<BcolAccountDetails> {
    return BcolService.validateBCOL(bcolProfile)
  }

  @Action({ rawError: true })
  public async isOrgNameAvailable (createRequestBody: CreateOrgRequestBody) {
    const response = await OrgService.isOrgNameAvailable(createRequestBody.name, createRequestBody.branchName)
    if (response.status === 204) {
      return true
    } else {
      return false
    }
  }

  @Action({ rawError: true })
  public async updateOrg (createRequestBody: CreateOrgRequestBody) {
    if (createRequestBody?.paymentInfo?.paymentMethod === PaymentTypes.CREDIT_CARD) {
      createRequestBody.paymentInfo.paymentMethod = PaymentTypes.DIRECT_PAY
    }
    const response = await OrgService.updateOrg(this.context.state['currentOrganization'].id, createRequestBody)
    this.context.commit('setCurrentOrganization', response.data)
    return response?.data
  }

  @Action({ rawError: true })
  public async createInvitation (invitation: CreateInvitationRequestBody) {
    try {
      const response = await InvitationService.createInvitation(invitation)
      if (!response || !response.data || response.status !== 201) {
        throw new Error('Unable to create invitation')
      }
      this.context.commit('addSentInvitation', response.data)
      this.context.dispatch('syncPendingOrgInvitations')
    } catch (exception) {
      this.context.commit('addFailedInvitation', invitation)
      throw exception
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
    this.context.dispatch('syncPendingOrgInvitations')
  }

  @Mutation
  public setInvalidTokenStatus (status:boolean) {
    this.invalidInvitationToken = status
  }

  @Mutation
  public setTokenErrorStatus (status:boolean) {
    this.tokenError = status
  }

  @Action({ rawError: true })
  public async validateInvitationToken (token: string): Promise<EmptyResponse> {
    try {
      const response = await InvitationService.validateToken(token)
      this.context.commit('setInvalidTokenStatus', false)
      this.context.commit('setTokenErrorStatus', false)
      return response && response.data ? response.data : undefined
    } catch (err) {
      if (err.response.status === 400 || err.response.status === 404) {
        this.context.commit('setTokenErrorStatus', false)
        this.context.commit('setInvalidTokenStatus', true)
      } else {
        this.context.commit('setTokenErrorStatus', true)
        this.context.commit('setInvalidTokenStatus', false)
      }
    }
  }

  @Action({ rawError: true })
  public async acceptInvitation (token: string): Promise<Invitation> {
    const response = await InvitationService.acceptInvitation(token)
    return response && response.data ? response.data : undefined
  }

  @Action({ rawError: true })
  public async deactivateOrg () {
    const response = await OrgService.deactivateOrg(this.context.state['currentOrganization'].id)

    // If no response, or error code, throw exception to be caught
    if (!response || response.status !== 204) {
      throw Error('Unable to dissolve organisation')
    }
  }

  @Action({ rawError: true })
  public async leaveTeam (memberId: number) {
    // Send request to remove member on server and get result
    const response = await OrgService.leaveOrg(this.context.state['currentOrganization'].id, memberId)

    // If no response, or error code, throw exception to be caught
    if (!response || response.status !== 200 || !response.data) {
      throw Error('Unable to delete member')
    } else {
      this.context.dispatch('syncActiveOrgMembers')
    }
  }

  @Action({ rawError: true })
  public async updateMember (updatePayload: UpdateMemberPayload) {
    // Send request to update member on server and get result
    const response = await OrgService.updateMember(this.context.state['currentOrganization'].id, updatePayload)

    // If no response or error, throw exception to be caught
    if (!response || response.status !== 200 || !response.data) {
      throw Error('Unable to update member role')
    } else {
      this.context.dispatch('syncActiveOrgMembers')
      this.context.dispatch('syncPendingOrgMembers')
      this.context.dispatch('syncMembership', this.context.state['currentOrganization'].id)
    }
  }

  @Action({ rawError: true })
  public async deleteUser (userId: string) {
    // Send request to update member on server and get result
    const response = await UserService.deleteAnonymousUser(userId)

    // If no response or error, throw exception to be caught
    if (!response || response.status !== 204) {
      throw Error('Unable to remove user')
    } else {
      this.context.dispatch('syncActiveOrgMembers')
      this.context.dispatch('syncPendingOrgMembers')
    }
  }

  @Action({ commit: 'setActiveOrgMembers', rawError: true })
  public async syncActiveOrgMembers () {
    const response = await OrgService.getOrgMembers(this.context.state['currentOrganization'].id, 'ACTIVE')
    return response.data && response.data.members ? response.data.members : []
  }

  @Action({ rawError: true })
  public async syncAddress () {
    const contact = await OrgService.getContactForOrg(this.context.state['currentOrganization'].id)
    // the contact model has lot of values which are not address..strip them off
    const address:Address = { region: contact?.region,
      city: contact?.city,
      postalCode: contact?.postalCode,
      country: contact?.country,
      street: contact?.street,
      streetAdditional: contact?.streetAdditional,
      deliveryInstructions: contact?.deliveryInstructions }
    this.context.commit('setCurrentOrganizationAddress', address)
  }

  @Action({ commit: 'setPendingOrgMembers', rawError: true })
  public async syncPendingOrgMembers () {
    const response = await OrgService.getOrgMembers(this.context.state['currentOrganization'].id, 'PENDING_APPROVAL')
    return response.data && response.data.members ? response.data.members : []
  }

  @Action({ commit: 'setPendingOrgInvitations', rawError: true })
  public async syncPendingOrgInvitations () {
    const response = await OrgService.getOrgInvitations(this.context.state['currentOrganization'].id, 'PENDING')
    return response.data && response.data.invitations ? response.data.invitations : []
  }

  @Action({ rawError: true })
  public async addProductsToOrg (productsRequestBody: ProductsRequestBody): Promise<Products> {
    const response = await StaffService.addProducts(this.context.state['currentOrganization'].id, productsRequestBody)
    return response?.data
  }

  @Action({ rawError: true })
  public async createUsers (addUserBody: AddUsersToOrgBody) {
    try {
      const response = await UserService.createUsers(addUserBody)
      if (!response || !response.data || ![200, 201, 207].includes(response.status) || !response.data?.users) {
        throw new Error('Unable to create users')
      } else {
        let users = response.data.users
        let successUsers: BulkUsersSuccess[] = []
        let failedUsers: BulkUsersFailed[] = []
        users.forEach((user) => {
          if (user.httpStatus === 201) {
            const password = (addUserBody.users.find(({ username }) => username === user.firstname))?.password
            successUsers.push({
              username: user.firstname,
              password: password
            })
          } else {
            failedUsers.push({
              username: user.username,
              error: user.error
            })
          }
        })
        this.context.commit('setCreatedUsers', successUsers)
        this.context.commit('setFailedUsers', failedUsers)
        await this.context.dispatch('syncActiveOrgMembers')
      }
    } catch (exception) {
      throw exception
    }
  }

  @Action({ rawError: true })
  public async resetPassword (addUserBody: AddUserBody) {
    await UserService.resetPassword(addUserBody.username, addUserBody.password)
    // setting so that it can be shown in the updated modal ;no other reason
    const successUsers: BulkUsersSuccess[] = [{ username: addUserBody.username, password: addUserBody.password }]
    this.context.commit('setCreatedUsers', successUsers)
    this.context.commit('setFailedUsers', [])
  }

  @Action({ commit: 'setCurrentOrgTransactionList', rawError: true })
  public async getTransactionList (filterParams: TransactionFilterParams) {
    const response = await PaymentService.getTransactions(this.context.state['currentOrganization'].id, filterParams)
    if (response?.data) {
      const formattedList = await this.formatTransactionTableData(response.data.items || [])
      return {
        limit: response.data.limit,
        page: response.data.page,
        total: response.data.total,
        transactionsList: formattedList
      }
    }
    return {}
  }

  @Action({ rawError: true })
  public async getTransactionReport (filterParams: TransactionFilter) {
    const response = await PaymentService.getTransactionReports(this.context.state['currentOrganization'].id, filterParams)
    return response?.data
  }

  // This function will be used to format the transaction response to a required table display format
  @Action({ rawError: true })
  private formatTransactionTableData (transactionList) {
    let transactionTableData = []
    transactionList.forEach(transaction => {
      let transactionNames = []
      transaction?.lineItems?.forEach(lineItem => {
        transactionNames.push(lineItem.description)
      })
      transactionTableData.push({
        id: transaction.id,
        transactionNames: transactionNames,
        folioNumber: transaction?.folioNumber || '',
        businessIdentifier: transaction?.businessIdentifier || '',
        initiatedBy: transaction.createdName,
        transactionDate: transaction.createdOn,
        totalAmount: (transaction?.total || 0).toFixed(2),
        status: transaction.statusCode,
        details: transaction.details || []
      })
    })
    return transactionTableData
  }

  @Action({ rawError: true })
  public async getStatementsList (filterParams: StatementFilterParams) {
    const response = await PaymentService.getStatementsList(this.context.state['currentOrganization'].id, filterParams)
    return response?.data
  }

  @Action({ rawError: true })
  public async getStatement (statementParams) {
    const response = await PaymentService.getStatement(this.context.state['currentOrganization'].id, statementParams.statementId, statementParams.type)
    return response || {}
  }

  @Action({ commit: 'setStatementSettings', rawError: true })
  public async fetchStatementSettings () {
    const response = await PaymentService.getStatementSettings(this.context.state['currentOrganization'].id)
    return response?.data || {}
  }

  @Action({ rawError: true })
  public async updateStatementSettings (statementFrequency) {
    const response = await PaymentService.updateStatementSettings(this.context.state['currentOrganization'].id, statementFrequency)
    return response?.data || {}
  }

  @Action({ commit: 'setStatementNotificationSettings', rawError: true })
  public async getStatementRecipients () {
    const response = await PaymentService.getStatementRecipients(this.context.state['currentOrganization'].id)
    return response?.data || {}
  }

  @Action({ rawError: true })
  public async updateStatementNotifications (statementNotification) {
    const response = await PaymentService.updateStatementNotifications(this.context.state['currentOrganization'].id, statementNotification)
    return response?.data || {}
  }

  @Action({ rawError: true })
  public async getOrgPayments (orgId?: number): Promise<OrgPaymentDetails> {
    const id = orgId || this.context.state['currentOrganization'].id
    // TODO can refator for performance improvment check on Transactions page getPaymentDetails method for sample code
    const response = await OrgService.getOrgPayments(id)
    let paymentType = response?.data?.futurePaymentMethod ? response?.data?.futurePaymentMethod : response?.data?.paymentMethod || undefined
    paymentType = (paymentType === PaymentTypes.DIRECT_PAY) ? PaymentTypes.CREDIT_CARD : paymentType
    this.context.commit('setCurrentOrganizationPaymentType', paymentType)
    // setting padinfo for showing details
    const padInfo = response?.data?.cfsAccount || {}
    this.context.commit('setCurrentOrganizationPADInfo', padInfo)
    this.context.commit('setCurrentOrganizationPaymentDetails', response?.data)
    return response?.data
  }

  @Action({ rawError: true })
  public async getFailedInvoices (): Promise<InvoiceList[]> {
    const response = await PaymentService.getFailedInvoices(this.context.state['currentOrganization'].id)
    // if there is any failed payment which is partially paid, return only that payment.
    let items = response?.data?.items || []
    items.forEach(payment => {
      if (payment.paidAmount > 0) {
        items = [payment]
      }
    })
    return items
  }

  // to calculate failed invoices. need to move appropriate place since its returning data than commiting to store (which is not standard)
  @Action({ rawError: true })
  public async calculateFailedInvoices () {
    let totalPaidAmount = 0
    let totalAmountToPay = 0
    let nsfCount = 0
    let nsfFee = 0
    let totalTransactionAmount = 0
    const failedInvoices: InvoiceList[] = await this.getFailedInvoices()
    failedInvoices?.forEach((failedInvoice) => {
      totalPaidAmount += failedInvoice?.paidAmount
      totalAmountToPay += failedInvoice?.invoices?.map(el => el.total).reduce((accumulator, invoiceTotal) => accumulator + invoiceTotal)
      failedInvoice?.invoices?.forEach((invoice) => {
        const nsfItems = invoice?.lineItems?.filter(lineItem => (lineItem.description === 'NSF'))
          .map(el => el.total)
        nsfCount += nsfItems.length
        nsfFee += (nsfItems.length) ? nsfItems?.reduce((accumulator, currentValue) => accumulator + currentValue) : 0
      })
    })
    totalTransactionAmount = totalAmountToPay - nsfFee
    totalAmountToPay = totalAmountToPay - totalPaidAmount
    return { totalTransactionAmount, totalAmountToPay, nsfFee, nsfCount }
  }

  @Action({ rawError: true })
  public async resetAccountSetupProgress (): Promise<void> {
    this.context.commit('setGrantAccess', false)
    this.context.commit('setCurrentOrganization', undefined)
    this.context.commit('setSelectedAccountType', undefined)
    this.context.commit('setCurrentOrganizationType', undefined)
    this.context.commit('setCurrentOrganizationPaymentType', undefined)
    this.context.commit('setCurrentOrganizationPADInfo', undefined)
    this.context.dispatch('resetoCurrentSelectedProducts')
  }

  @Action({ rawError: true })
  public async resetAccountWhileSwitchingPremium (): Promise<void> {
    this.context.commit('setGrantAccess', false)
    // need to keep accesstype while resetting to know whenther the account is GOVM or not.
    this.context.commit('setCurrentOrganization', { ...this.context.state['currentOrganization'], ...{ name: '' } })
    this.context.commit('setCurrentOrganizationAddress', undefined)
    this.context.commit('setCurrentOrganizationPaymentType', undefined)
    this.context.commit('setCurrentOrganizationPADInfo', undefined)
  }

  @Action({ rawError: true })
  public async createAccountPayment () {
    const response = await PaymentService.createAccountPayment(this.context.state['currentOrganization'].id)
    return response?.data || {}
  }

  @Action({ rawError: true })
  public async createTransaction (transactionData) {
    const response = await PaymentService.createTransaction(transactionData.paymentId, transactionData.redirectUrl)
    return response?.data || {}
  }

  @Action({ rawError: true })
  public async getInvoice (invoicePayload) {
    const response = await PaymentService.getInvoice(invoicePayload.invoiceId, invoicePayload.accountId)
    return response?.data || {}
  }

  @Action({ rawError: true })
  public async updateInvoicePaymentMethodAsCreditCard (invoicePayload) {
    const response = await PaymentService.updateInvoicePaymentMethodAsCreditCard(invoicePayload.paymentId, invoicePayload.accountId)
    return response?.data || {}
  }

  @Action({ rawError: true })
  public async downloadOBInvoice (paymentId: string) {
    const response = await PaymentService.downloadOBInvoice(paymentId)
    return response || {}
  }

  @Action({ rawError: true })
  public async getOrganizationForAffiliate (): Promise<Organization> {
    const businessIdentifier = ConfigHelper.getFromSession(SessionStorageKeys.BusinessIdentifierKey)
    const response = await OrgService.getOrgForAffiliate(businessIdentifier)
    const organization = response?.data?.orgs[0]
    return organization
  }

  @Action({ commit: 'setProductList', rawError: true })
  public async getOrgProducts (orgId:number): Promise<OrgProduct[]> {
    const response = await OrgService.getProducts(orgId)
    return response?.data
  }

  @Action({ rawError: true })
  public async addOrgProducts (productsRequestBody: OrgProductsRequestBody): Promise<OrgProduct> {
    const orgId = this.context.state['currentOrganization']?.id
    const response = await OrgService.addProducts(orgId, productsRequestBody)
    return response?.data
  }

  @Action({ commit: 'setProductList', rawError: true })
  public async getProductList (): Promise<OrgProduct[]> {
    const response:any = await OrgService.avialbelProducts()
    if (response && response.data && response.status === 200) {
      return response.data
    }
    return []
  }

  @Action({ rawError: true })
  public async addToCurrentSelectedProducts ({ productCode, forceRemove = false }): Promise<any> {
    const currentSelectedProducts = this.context.state['currentSelectedProducts']
    const isAlreadySelected = currentSelectedProducts.includes(productCode)

    let productList = []
    // removing from array if already existing (unselecting)
    // forceRemove will be used to remove when user didn't accept TOS
    // also no need to push if user didnt accept TOS
    if (isAlreadySelected || forceRemove) {
      productList = currentSelectedProducts.filter(code => code !== productCode)
    } else {
      productList = [...currentSelectedProducts, productCode]
    }
    this.context.commit('setCurrentSelectedProducts', productList)
    this.context.dispatch('currentSelectedProductsPremiumOnly')
  }

  @Action({ rawError: true })
  public async resetoCurrentSelectedProducts (): Promise<any> {
    this.context.commit('setCurrentSelectedProducts', [])
    this.context.dispatch('currentSelectedProductsPremiumOnly')
  }

  // set product with subscriptionStatus active to selected product
  @Action({ rawError: true })
  public async setSubscribedProducts (): Promise<any> {
    const productList = this.context.state['productList']
    let currentSelectedProducts = []
    currentSelectedProducts = productList.filter(product => product.subscriptionStatus === ProductStatus.ACTIVE).map((prod) => (prod.code))
    this.context.commit('setCurrentSelectedProducts', currentSelectedProducts)
  }

  @Action({ commit: 'setIsCurrentSelectedProductsPremiumOnly', rawError: true })
  public async currentSelectedProductsPremiumOnly (): Promise<any> {
    const currentSelectedProducts = this.context.state['currentSelectedProducts']
    const productList = this.context.state['productList']

    let isPremiumOnly = false
    if (currentSelectedProducts.length > 0) {
      isPremiumOnly = productList.some(product => product.premiumOnly && currentSelectedProducts.includes(product.code))
    }

    return isPremiumOnly
  }

  @Action({ commit: 'setCurrentOrganizationGLInfo', rawError: true })
  public async fetchCurrentOrganizationGLInfo (accountId: number): Promise<any> {
    const response = await PaymentService.getRevenueAccountDetails(accountId)
    if (response?.data?.revenueAccount) {
      const revenueAccount = response?.data?.revenueAccount
      return {
        client: revenueAccount.client,
        responsibilityCentre: revenueAccount.responsibilityCentre,
        serviceLine: revenueAccount.serviceLine,
        stob: revenueAccount.stob,
        projectCode: revenueAccount.projectCode
      }
    }
    return {}
  }

  @Action({ commit: 'setOrgProductFeeCodes', rawError: true })
  public async fetchOrgProductFeeCodes (): Promise<OrgProductFeeCode[]> {
    const response = await PaymentService.getOrgProductFeeCodes()
    if (response?.data?.codes && response?.data?.codes.length !== 0) {
      const unfilteredOrgProductFeeCodes = response.data.codes
      return unfilteredOrgProductFeeCodes.filter((orgProductFeeCode: OrgProductFeeCode) => {
        const code = orgProductFeeCode.code
        if (code.startsWith(FeeCodes.PPR_CHANGE_OR_AMENDMENT)) {
          return orgProductFeeCode
        }
      })
    }
    return []
  }

  @Action({ rawError: true })
  public async createAccountFees (accoundId:number): Promise<any> {
    const accountFeePayload = JSON.parse(JSON.stringify(this.context.state['currentAccountFees']))
    await PaymentService.createAccountFees(accoundId.toString(), { accountFees: accountFeePayload })
  }

  @Action({ rawError: true })
  public async updateAccountFees (accountFee): Promise<any> {
    const { accoundId, accountFees } = accountFee
    const response = await PaymentService.updateAccountFees(accoundId.toString(), accountFees)
    if (response && response.data && response.status === 200) {
      return response.data
    }
  }

  @Action({ commit: 'setCurrentAccountFees', rawError: true })
  public async syncCurrentAccountFees (accoundId:number): Promise<AccountFee[]> {
    const response = await PaymentService.getAccountFees(accoundId.toString())
    if (response && response.data && response.status === 200) {
      return response.data.accountFees
    }
  }

  @Action({ rawError: true })
  public async getOrgNameAutoComplete (searchValue: string): Promise<AutoCompleteResponse> {
    if (!searchValue) {
      return
    }
    return VonService.getOrgNameAutoComplete(searchValue)
      .then(response => {
        const data = response?.data
        if (!data) {
          throw new Error('Invalid API response')
        }
        return data
      }).catch(error => {
        return error
      })
  }

  @Action({ rawError: true })
  public async getOrgAdminContact (orgId: number): Promise<Address> {
    const response = await OrgService.getContactForOrg(orgId)
    return response
  }

  // Check if user has any accounts, if any, default the first returned value as the selected org.
  @Action({ rawError: true })
  public async setCurrentOrganizationFromUserAccountSettings (): Promise<void> {
    const response = await UserService.getUserAccountSettings(this.context.rootState.user.userProfile?.keycloakGuid)
    if (response && response.data) {
      // filter by account type and default first returned value as the current organization
      const orgs = response.data.filter(userSettings => (userSettings.type === 'ACCOUNT'))
      if (orgs && orgs.length) {
        const orgId = +orgs[0].id
        // sync org and add to session
        await this.syncOrganization(orgId)
        await this.addOrgSettings(this.context.state['currentOrganization'])
      }
    }
  }

  @Action({ rawError: true })
  public async getOrgApiKeys (orgId) {
    const response = await OrgService.getOrgApiKeys(orgId)
    return response?.data || {}
  }

  @Action({ rawError: true })
  public async revokeOrgApiKeys (ApiDetails) {
    const response = await OrgService.revokeOrgApiKeys(ApiDetails)
    return response?.data || {}
  }

  @Action({ rawError: true })
  public async updateOrganizationAccessType (accessType: string) {
    const orgId = this.context.state['currentOrganization']?.id
    if (orgId && accessType) {
      try {
        const patchOrgPayload: PatchOrgPayload = {
          action: PatchActions.UPDATE_ACCESS_TYPE,
          accessType: accessType
        }
        const response = await OrgService.patchOrg(orgId, patchOrgPayload)
        if (response && response.status === 200) {
          await this.context.dispatch('syncOrganization', orgId)
        }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('update Organization AccessType operation failed! - ', error)
      }
    }
  }
}
