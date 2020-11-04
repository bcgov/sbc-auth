import { Account, Actions, LoginSource, Pages, Role, SessionStorageKeys } from '@/util/constants'
import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import {
  AddUserBody,
  AddUsersToOrgBody,
  BulkUsersFailed,
  BulkUsersSuccess,
  CreateRequestBody as CreateOrgRequestBody,
  CreateRequestBody,
  Member,
  MembershipStatus,
  MembershipType,
  Organization,
  PADInfo,
  PADInfoValidation,
  UpdateMemberPayload
} from '@/models/Organization'
import { BcolAccountDetails, BcolProfile } from '@/models/bcol'
import { CreateRequestBody as CreateInvitationRequestBody, Invitation } from '@/models/Invitation'
import { Products, ProductsRequestBody } from '@/models/Staff'
import { StatementFilterParams, StatementListItem, StatementNotificationSettings, StatementSettings } from '@/models/statement'
import { TransactionFilter, TransactionFilterParams, TransactionTableList, TransactionTableRow } from '@/models/transaction'
import { AccountSettings } from '@/models/account-settings'
import { Address } from '@/models/address'
import BcolService from '@/services/bcol.services'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { EmptyResponse } from '@/models/global'
import InvitationService from '@/services/invitation.services'
import KeyCloakService from 'sbc-common-components/src/services/keycloak.services'
import OrgService from '@/services/org.services'
import PaymentService from '@/services/payment.services'
import PermissionService from '@/services/permission.services'
import StaffService from '@/services/staff.services'
import UserService from '@/services/user.services'
import { UserSettings } from 'sbc-common-components/src/models/userSettings'

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
  accountTypeBeforeChange = '' // used for detecting the original type of the account which is getting down/up graded
  permissions: string[] = []
  accessType: string
  memberLoginOption = ''

  currentStatementNotificationSettings: StatementNotificationSettings = {} as StatementNotificationSettings
  currentOrgTransactionList: TransactionTableRow[] = []
  statementSettings: StatementSettings = {} as StatementSettings

  @Mutation
  public setAccessType (accessType:string) {
    this.accessType = accessType
  }

  @Mutation
  public setMemberLoginOption (memberLoginOption:string) {
    this.memberLoginOption = memberLoginOption
  }

  @Mutation
  public setAccountTypeBeforeChange (accountTypeBeforeChange:string) {
    this.accountTypeBeforeChange = accountTypeBeforeChange
  }

  @Mutation
  public setGrantAccess (grantAccess: boolean) {
    if (this.currentOrganization) {
      this.currentOrganization.grantAccess = grantAccess
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
  public setCurrentOrganizationPaymentType (paymentType: string) {
    this.currentOrgPaymentType = paymentType
  }

  @Mutation
  public setCurrentOrganizationType (orgType: string) {
    this.currentOrganizationType = orgType
  }

  @Mutation
  public setCurrentOrganizationPADInfo (padInfo: PADInfo) {
    this.currentOrgPADInfo = padInfo
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
      const res = await PermissionService.getPermissions(membership.membershipTypeCode)
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
  public async changeOrgType (action:Actions): Promise<Organization> {
    const org:Organization = this.context.state['currentOrganization']
    let createRequestBody: CreateRequestBody = {
      name: org.name,
      typeCode: org.orgType
    }
    if (org.orgType === Account.PREMIUM) {
      createRequestBody.bcOnlineCredential = org.bcolProfile
      createRequestBody.mailingAddress = this.context.state['currentOrgAddress']
    }
    const response = await OrgService.upgradeOrDowngradeOrg(createRequestBody, org.id, action)
    const organization = response?.data
    this.context.commit('setCurrentOrganization', organization)
    this.context.commit('setAccountTypeBeforeChange', organization.orgType)
    return response?.data
  }

  @Action({ rawError: true })
  public async createOrg (): Promise<Organization> {
    const org: Organization = this.context.state['currentOrganization']
    const address = this.context.state['currentOrgAddress']
    const paymentMethod = this.context.state['currentOrgPaymentType']
    const padInfo: PADInfo = this.context.state['currentOrgPADInfo']

    const createRequestBody: CreateRequestBody = {
      name: org.name,
      accessType: this.context.state['accessType'],
      typeCode: org.orgType
    }
    if (org.bcolProfile) {
      createRequestBody.bcOnlineCredential = org.bcolProfile
    }
    if (address) {
      createRequestBody.mailingAddress = address
    }
    if (paymentMethod) {
      createRequestBody.paymentInfo = {
        paymentMethod: paymentMethod
      }
    }
    if (padInfo && createRequestBody.paymentInfo) {
      createRequestBody.paymentInfo.bankTransitNumber = padInfo.bankTransitNumber
      createRequestBody.paymentInfo.bankInstitutionNumber = padInfo.bankInstitutionNumber
      createRequestBody.paymentInfo.bankAccountNumber = padInfo.bankAccountNumber
    }
    const response = await OrgService.createOrg(createRequestBody)
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
      accountType: org?.orgType
    }
    ConfigHelper.addToSession(SessionStorageKeys.CurrentAccount, JSON.stringify(accountSettings))
    return accountSettings
  }

  @Action({ rawError: true })
  public async validateBcolAccount (bcolProfile: BcolProfile): Promise<BcolAccountDetails> {
    return BcolService.validateBCOL(bcolProfile)
  }

  @Action({ rawError: true })
  public async isOrgNameAvailable (name: string) {
    const response = await OrgService.isOrgNameAvailable(name)
    if (response.status === 204) {
      return true
    } else {
      return false
    }
  }

  @Action({ rawError: true })
  public async updateOrg (createRequestBody: CreateOrgRequestBody) {
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
  public async dissolveTeam () {
    // Send request to remove member on server and get result
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
      streetAdditional: contact?.streetAdditional }
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
        status: transaction.statusCode
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
  public async getOrgPayments () {
    const response = await OrgService.getOrgPayments(this.context.state['currentOrganization'].id)
    const paymentType = response?.data?.paymentMethod || undefined
    this.context.commit('setCurrentOrganizationPaymentType', paymentType)
    return response?.data
  }

  @Action({ rawError: true })
  public async resetAccountSetupProgress (): Promise<void> {
    this.context.commit('setGrantAccess', false)
    this.context.commit('setCurrentOrganization', undefined)
    this.context.commit('setSelectedAccountType', undefined)
    this.context.commit('setCurrentOrganizationType', undefined)
    this.context.commit('setCurrentOrganizationPaymentType', undefined)
    this.context.commit('setCurrentOrganizationPADInfo', undefined)
  }

  @Action({ rawError: true })
  public async resetAccountWhileSwitchingPremium (): Promise<void> {
    this.context.commit('setGrantAccess', false)
    this.context.commit('setCurrentOrganization', { name: '' })
    this.context.commit('setCurrentOrganizationAddress', undefined)
    this.context.commit('setCurrentOrganizationPaymentType', undefined)
    this.context.commit('setCurrentOrganizationPADInfo', undefined)
  }
}
