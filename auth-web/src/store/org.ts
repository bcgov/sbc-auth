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
  CFSAccountDetails,
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
import { BcolAccountDetails, BcolProfile } from '@/models/bcol'
import { CreateRequestBody as CreateInvitationRequestBody, Invitation } from '@/models/Invitation'
import { Products, ProductsRequestBody } from '@/models/Staff'
import { StatementFilterParams, StatementNotificationSettings, StatementSettings } from '@/models/statement'
import { computed, reactive, toRefs } from '@vue/composition-api'
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
import { defineStore } from 'pinia'
import { useUserStore } from './user'

export const useOrgStore = defineStore('org', () => {
  const userStore = useUserStore()
  const state = reactive({
    list: [] as Organization[],
    resending: false,
    sentInvitations: [] as Invitation[],
    failedInvitations: [] as Invitation[],
    currentAccountSettings: undefined as AccountSettings,
    currentOrganization: undefined as Organization,
    currentOrgAddress: undefined as Address,
    currentOrgPaymentType: undefined as string,
    currentOrgPADInfo: undefined as PADInfo,
    currentOrganizationType: undefined as string,
    currentMembership: undefined as Member,
    activeOrgMembers: [] as Member[],
    pendingOrgMembers: [] as Member[],
    pendingOrgInvitations: [] as Invitation[],
    invalidInvitationToken: false,
    tokenError: false,
    createdUsers: [] as BulkUsersSuccess[],
    failedUsers: [] as BulkUsersFailed[],
    permissions: [] as string[],
    accessType: undefined as string,
    memberLoginOption: '' as string,
    currentOrgGLInfo: undefined as GLInfo,
    productList: [] as OrgProduct[], // list of all products
    currentSelectedProducts: [] as any, // selected product list code in array
    currentStatementNotificationSettings: {} as StatementNotificationSettings,
    statementSettings: {} as StatementSettings,
    orgProductFeeCodes: [] as OrgProductFeeCode[],
    currentAccountFees: [] as AccountFee[],
    currentOrgPaymentDetails: null as OrgPaymentDetails,
    isCurrentSelectedProductsPremiumOnly: false,
    resetAccountTypeOnSetupAccount: false, // this flag use to check need to reset accounttype select when moving back and forth in stepper
    vDisplayModeValue: ''// DisplayModeValues.VIEW_ONLY
  })

  /** Is True if the current account is premium. */
  const isPremiumAccount = computed<boolean>(() => {
    return state.currentOrganization?.orgType === Account.PREMIUM
  })

  const canEditBusinessInfo = computed<boolean>(() => {
    return [Permission.EDIT_BUSINESS_INFO].some(per => state.permissions.includes(per))
  })

  const needMissingBusinessDetailsRedirect = computed<boolean>(() => {
    return typeof (state.currentOrganization?.isBusinessAccount) === 'undefined' &&
      state.currentOrganization?.accessType !== AccessType.GOVM &&
      canEditBusinessInfo.value
  })

  const isBusinessAccount = computed<boolean>(() => {
    return state.currentOrganization?.isBusinessAccount === true
  })

  function setAccessType (accessType:string) {
    state.accessType = accessType
  }

  function setMemberLoginOption (memberLoginOption:string) {
    state.memberLoginOption = memberLoginOption
  }

  function setGrantAccess (grantAccess: boolean) {
    if (state.currentOrganization) {
      state.currentOrganization = { ...state.currentOrganization, grantAccess }
    }
  }

  function resetCurrentOrganisation () {
    state.currentOrganization = { name: '' }
  }

  function resetBcolDetails () {
    state.currentOrganization.bcolProfile = undefined
    state.currentOrganization.bcolAccountDetails = undefined
    state.currentOrgAddress = undefined
  }

  function setSelectedAccountType (selectedAccountType: Account | undefined) {
    if (state.currentOrganization) {
      state.currentOrganization.orgType = selectedAccountType
    }
  }

  function setCurrentAccountSettings (accountSettings: AccountSettings) {
    state.currentAccountSettings = accountSettings
  }

  function resetInvitations () {
    state.resending = false
    state.sentInvitations = []
    state.failedInvitations = []
  }

  function setCurrentOrganization (organization: Organization | undefined) {
    state.currentOrganization = organization
    // for keeping a constant format for BCOL account banner
    if (organization?.bcolAccountId && organization?.bcolUserId) {
      state.currentOrganization.bcolAccountDetails = {
        accountNumber: organization.bcolAccountId,
        userId: organization.bcolUserId
      }
    }
  }

  function setCurrentMembership (membership: Member) {
    state.currentMembership = membership
  }

  function setCurrentOrganizationAddress (address: Address | undefined) {
    state.currentOrgAddress = (address) ? JSON.parse(JSON.stringify(address)) : undefined
  }

  function setCurrentOrganizationName (name: string) {
    state.currentOrganization.name = name
  }

  function setCurrentOrganizationPaymentType (paymentType: string) {
    state.currentOrgPaymentType = paymentType
  }

  function setCurrentOrganizationType (orgType: string) {
    state.currentOrganizationType = orgType
  }

  function setCurrentOrganizationPADInfo (padInfo: PADInfo) {
    state.currentOrgPADInfo = padInfo
  }

  function setCurrentOrganizationGLInfo (glInfo: GLInfo) {
    state.currentOrgGLInfo = glInfo
  }

  function setCurrentAccountFees (accountFee: AccountFee[]) {
    state.currentAccountFees = accountFee
  }

  function setResetAccountTypeOnSetupAccount (resetAccountTypeOnSetupAccount:boolean) {
    state.resetAccountTypeOnSetupAccount = resetAccountTypeOnSetupAccount
  }

  function setViewOnlyMode (viewOnlyModeValue:string) {
    state.vDisplayModeValue = viewOnlyModeValue
  }

  function setCurrentOrganizationBusinessType (orgBusinessType: OrgBusinessType) {
    state.currentOrganization = { ...state.currentOrganization, ...orgBusinessType }
  }

  function setCurrentOrganizationBcolProfile (bcolProfile: BcolProfile) {
    state.currentOrganization = { ...state.currentOrganization, bcolProfile }
  }

  async function resetCurrentOrganization (): Promise<void> {
    setCurrentOrganization(undefined)
    state.activeOrgMembers = []
    state.pendingOrgMembers = []
    state.pendingOrgInvitations = []
  }

  async function syncOrganization (orgId: number): Promise<Organization> {
    const response = await OrgService.getOrganization(orgId)
    const organization = response?.data
    setCurrentOrganization(organization)
    return organization
  }

  async function suspendOrganization (suspensionReasonCode: string) {
    const orgId = state.currentOrganization?.id
    const orgStatus = state.currentOrganization.statusCode === AccountStatus.ACTIVE ? AccountStatus.SUSPENDED : AccountStatus.ACTIVE
    if (orgId && orgStatus) {
      try {
        const patchOrgPayload: PatchOrgPayload = {
          action: PatchActions.UPDATE_STATUS,
          statusCode: orgStatus,
          suspensionReasonCode: suspensionReasonCode
        }
        const response = await OrgService.patchOrg(orgId, patchOrgPayload)
        if (response.status === 200) {
          await syncOrganization(orgId)
        }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Suspend/Unsuspend Account operation failed! - ', error)
      }
    }
  }

  async function syncMemberLoginOption (orgId: number): Promise<string> {
    const response = await OrgService.getMemberLoginOption(orgId)
    setMemberLoginOption(response)
    return response
  }

  async function syncMembership (orgId: number): Promise<Member> {
    let permissions:string[] = []
    let response
    let membership:Member = null
    const kcUserProfile = KeyCloakService.getUserInfo()
    if (!kcUserProfile.roles.includes(Role.Staff)) {
      response = await UserService.getMembership(orgId)
      membership = response?.data
      // const org: Organization = state.currentOrganization']
      const currentAccountSettings = state.currentAccountSettings
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
    state.currentMembership = membership
    state.permissions = permissions
    return response?.data
  }

  /*
   * staff doesnt need any other store set up's since he doesnt belong to an account
   * So a minimal method to create org
   */
  async function createOrgByStaff (createRequestBody: CreateOrgRequestBody): Promise<Organization> {
    const response = await OrgService.createOrg(createRequestBody)
    const result = response?.data
    setCurrentOrganization(result)
    return result
  }

  async function updateLoginOption (loginOption: string): Promise<string> {
    const org:Organization = state.currentOrganization
    const newLoginOption = await OrgService.updateMemberLoginOption(org.id, loginOption)
    setMemberLoginOption(loginOption)
    return newLoginOption
  }

  async function createOrg (): Promise<Organization> {
    const org: Organization = state.currentOrganization
    const address = state.currentOrgAddress
    const paymentMethod = state.currentOrgPaymentType
    const padInfo: PADInfo = state.currentOrgPADInfo

    const currentSelectedProducts = state.currentSelectedProducts
    // setting product subscriptions in required format
    const productsSelected: [] = currentSelectedProducts.map((code) => {
      return {
        productCode: code
      }
    })

    const createRequestBody: CreateRequestBody = {
      name: org.name,
      accessType: state.accessType,
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
    setCurrentOrganization(organization)
    await resetoCurrentSelectedProducts()
    await addOrgSettings(organization)
    return response?.data
  }

  async function createGovmOrg (): Promise<Organization> {
    const org: Organization = state.currentOrganization
    const address = state.currentOrgAddress
    const revenueAccount: GLInfo = state.currentOrgGLInfo
    const currentSelectedProducts = state.currentSelectedProducts
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
    setCurrentOrganization(organization)
    await addOrgSettings(organization)
    return response?.data
  }

  async function validatePADInfo (): Promise<PADInfoValidation> {
    const padInfo: PADInfo = { ...state.currentOrgPADInfo }
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

  async function addOrgSettings (org: Organization): Promise<UserSettings> {
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

  async function validateBcolAccount (bcolProfile: BcolProfile): Promise<BcolAccountDetails> {
    return BcolService.validateBCOL(bcolProfile)
  }

  async function isOrgNameAvailable (createRequestBody: CreateOrgRequestBody) {
    const response = await OrgService.isOrgNameAvailable(createRequestBody.name, createRequestBody.branchName)
    if (response.status === 204) {
      return true
    } else {
      return false
    }
  }

  async function updateOrg (createRequestBody: CreateOrgRequestBody) {
    if (createRequestBody?.paymentInfo?.paymentMethod === PaymentTypes.CREDIT_CARD) {
      createRequestBody.paymentInfo.paymentMethod = PaymentTypes.DIRECT_PAY
    }
    const response = await OrgService.updateOrg(state.currentOrganization.id, createRequestBody)
    setCurrentOrganization(response.data)
    return response?.data
  }

  async function createInvitation (invitation: CreateInvitationRequestBody) {
    try {
      const response = await InvitationService.createInvitation(invitation)
      if (!response?.data || response.status !== 201) {
        throw new Error('Unable to create invitation')
      }
      state.sentInvitations.push(response.data)
      await syncPendingOrgInvitations()
    } catch (exception) {
      state.failedInvitations.push(invitation as Invitation)
      throw exception
    }
  }

  async function resendInvitation (invitation: Invitation) {
    resetInvitations()
    state.resending = true
    try {
      await InvitationService.resendInvitation(invitation)
      state.sentInvitations.push(invitation)
    } catch (exception) {
      state.failedInvitations.push(invitation)
    }
  }

  async function deleteInvitation (invitationId: number) {
    const response = await InvitationService.deleteInvitation(invitationId)
    if (!response || response.status !== 200 || !response.data) {
      throw Error('Unable to delete invitation')
    }
    await syncPendingOrgInvitations()
  }

  async function validateInvitationToken (token: string): Promise<EmptyResponse> {
    try {
      const response = await InvitationService.validateToken(token)
      state.invalidInvitationToken = false
      state.tokenError = false
      return response?.data ? response.data : undefined
    } catch (err) {
      if (err.response.status === 400 || err.response.status === 404) {
        state.tokenError = false
        state.invalidInvitationToken = true
      } else {
        state.tokenError = true
        state.invalidInvitationToken = false
      }
    }
  }

  async function acceptInvitation (token: string): Promise<Invitation> {
    const response = await InvitationService.acceptInvitation(token)
    return response?.data ? response.data : undefined
  }

  async function deactivateOrg () {
    const response = await OrgService.deactivateOrg(state.currentOrganization.id)

    // If no response, or error code, throw exception to be caught
    if (!response || response.status !== 204) {
      throw Error('Unable to dissolve organisation')
    }
  }

  async function leaveTeam (memberId: number) {
    // Send request to remove member on server and get result
    const response = await OrgService.leaveOrg(state.currentOrganization.id, memberId)

    // If no response, or error code, throw exception to be caught
    if (!response || response.status !== 200 || !response.data) {
      throw Error('Unable to delete member')
    } else {
      await syncActiveOrgMembers()
    }
  }

  async function updateMember (updatePayload: UpdateMemberPayload) {
    // Send request to update member on server and get result
    const response = await OrgService.updateMember(state.currentOrganization.id, updatePayload)

    // If no response or error, throw exception to be caught
    if (!response || response.status !== 200 || !response.data) {
      throw Error('Unable to update member role')
    } else {
      await syncActiveOrgMembers()
      await syncPendingOrgMembers()
      await syncMembership(state.currentOrganization.id)
    }
  }

  async function deleteUser (userId: string) {
    // Send request to update member on server and get result
    const response = await UserService.deleteAnonymousUser(userId)

    // If no response or error, throw exception to be caught
    if (!response || response.status !== 204) {
      throw Error('Unable to remove user')
    } else {
      await syncActiveOrgMembers()
      await syncPendingOrgMembers()
    }
  }

  async function syncActiveOrgMembers () {
    const response = await OrgService.getOrgMembers(state.currentOrganization.id, 'ACTIVE')
    const result = response?.data?.members || []
    state.activeOrgMembers = result
    return result
  }

  async function syncAddress () {
    const contact = await OrgService.getContactForOrg(state.currentOrganization.id)
    // the contact model has lot of values which are not address..strip them off
    const address:Address = { region: contact?.region,
      city: contact?.city,
      postalCode: contact?.postalCode,
      country: contact?.country,
      street: contact?.street,
      streetAdditional: contact?.streetAdditional,
      deliveryInstructions: contact?.deliveryInstructions }
    setCurrentOrganizationAddress(address)
  }

  async function syncPendingOrgMembers () {
    const response = await OrgService.getOrgMembers(state.currentOrganization.id, 'PENDING_APPROVAL')
    const result = response?.data?.members || []
    state.pendingOrgMembers = result
    return result
  }

  async function syncPendingOrgInvitations () {
    const response = await OrgService.getOrgInvitations(state.currentOrganization.id, 'PENDING')
    const result = response?.data?.invitations || []
    state.pendingOrgInvitations = result
    return result
  }

  async function addProductsToOrg (productsRequestBody: ProductsRequestBody): Promise<Products> {
    const response = await StaffService.addProducts(state.currentOrganization.id, productsRequestBody)
    return response?.data
  }

  async function createUsers (addUserBody: AddUsersToOrgBody) {
    const response = await UserService.createUsers(addUserBody)
    if (!response?.data || ![200, 201, 207].includes(response.status) || !response.data?.users) {
      throw new Error('Unable to create users')
    } else {
      const users = response.data.users
      const successUsers: BulkUsersSuccess[] = []
      const failedUsers: BulkUsersFailed[] = []
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
      state.createdUsers = successUsers
      state.failedUsers = failedUsers
      await syncActiveOrgMembers()
    }
  }

  async function resetPassword (addUserBody: AddUserBody) {
    await UserService.resetPassword(addUserBody.username, addUserBody.password)
    // setting so that it can be shown in the updated modal ;no other reason
    const successUsers: BulkUsersSuccess[] = [{ username: addUserBody.username, password: addUserBody.password }]
    state.createdUsers = successUsers
    state.failedUsers = []
  }

  async function getStatementsList (filterParams: StatementFilterParams) {
    const response = await PaymentService.getStatementsList(state.currentOrganization.id, filterParams)
    return response?.data
  }

  async function getStatement (statementParams) {
    const response = await PaymentService.getStatement(state.currentOrganization.id, statementParams.statementId, statementParams.type)
    return response || {}
  }

  async function fetchStatementSettings () {
    const response = await PaymentService.getStatementSettings(state.currentOrganization.id)
    const result = response?.data || {} as StatementSettings
    state.statementSettings = result
    return result
  }

  async function updateStatementSettings (statementFrequency) {
    const response = await PaymentService.updateStatementSettings(state.currentOrganization.id, statementFrequency)
    return response?.data || {}
  }

  async function getStatementRecipients () {
    const response = await PaymentService.getStatementRecipients(state.currentOrganization.id)
    const result = response?.data || {} as StatementNotificationSettings
    state.currentStatementNotificationSettings = result
    return result
  }

  async function updateStatementNotifications (statementNotification) {
    const response = await PaymentService.updateStatementNotifications(state.currentOrganization.id, statementNotification)
    return response?.data || {}
  }

  async function getOrgPayments (orgId?: number): Promise<OrgPaymentDetails> {
    const id = orgId || state.currentOrganization.id
    const response = await OrgService.getOrgPayments(id)
    let paymentType = response?.data?.futurePaymentMethod ? response?.data?.futurePaymentMethod : response?.data?.paymentMethod || undefined
    paymentType = (paymentType === PaymentTypes.DIRECT_PAY) ? PaymentTypes.CREDIT_CARD : paymentType
    setCurrentOrganizationPaymentType(paymentType)
    // setting padinfo for showing details
    const padInfo = response?.data?.cfsAccount || {} as CFSAccountDetails
    setCurrentOrganizationPADInfo(padInfo)
    state.currentOrgPaymentDetails = response?.data
    return response?.data
  }

  async function getFailedInvoices (): Promise<InvoiceList[]> {
    const response = await PaymentService.getFailedInvoices(state.currentOrganization.id)
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
  async function calculateFailedInvoices () {
    let totalPaidAmount = 0
    let totalAmountToPay = 0
    let nsfCount = 0
    let nsfFee = 0
    let totalTransactionAmount = 0
    const failedInvoices: InvoiceList[] = await getFailedInvoices()
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

  async function resetAccountSetupProgress (): Promise<void> {
    setGrantAccess(false)
    setCurrentOrganization(undefined)
    setSelectedAccountType(undefined)
    setCurrentOrganizationType(undefined)
    setCurrentOrganizationPaymentType(undefined)
    setCurrentOrganizationPADInfo(undefined)
    await resetoCurrentSelectedProducts()
  }

  async function resetAccountWhileSwitchingPremium (): Promise<void> {
    setGrantAccess(false)
    // need to keep accesstype while resetting to know whenther the account is GOVM or not.
    setCurrentOrganization({ ...state.currentOrganization, ...{ name: '' } })
    setCurrentOrganizationAddress(undefined)
    setCurrentOrganizationPaymentType(undefined)
    setCurrentOrganizationPADInfo(undefined)
  }

  async function createAccountPayment () {
    const response = await PaymentService.createAccountPayment(state.currentOrganization.id)
    return response?.data || {}
  }

  async function createTransaction (transactionData) {
    const response = await PaymentService.createTransaction(transactionData.paymentId, transactionData.redirectUrl)
    return response?.data || {}
  }

  async function getInvoice (invoicePayload) {
    const response = await PaymentService.getInvoice(invoicePayload.invoiceId, invoicePayload.accountId)
    return response?.data || {}
  }

  async function updateInvoicePaymentMethodAsCreditCard (invoicePayload) {
    const response = await PaymentService.updateInvoicePaymentMethodAsCreditCard(invoicePayload.paymentId, invoicePayload.accountId)
    return response?.data || {}
  }

  async function downloadOBInvoice (paymentId: string) {
    const response = await PaymentService.downloadOBInvoice(paymentId)
    return response || {}
  }

  async function getOrganizationForAffiliate (): Promise<Organization> {
    const businessIdentifier = ConfigHelper.getFromSession(SessionStorageKeys.BusinessIdentifierKey)
    const response = await OrgService.getOrgForAffiliate(businessIdentifier)
    const organization = response?.data?.orgs[0]
    return organization
  }

  async function getOrgProducts (orgId:number): Promise<OrgProduct[]> {
    const response = await OrgService.getProducts(orgId)
    const result = response?.data
    state.productList = result
    return result
  }

  async function addOrgProducts (productsRequestBody: OrgProductsRequestBody): Promise<OrgProduct> {
    const orgId = state.currentOrganization?.id
    const response = await OrgService.addProducts(orgId, productsRequestBody)
    return response?.data
  }

  async function getProductList (): Promise<OrgProduct[]> {
    const response:any = await OrgService.avialbelProducts()
    if (response?.data && response.status === 200) {
      const result = response.data
      state.productList = result
      return result
    }
    state.productList = []
    return []
  }

  async function addToCurrentSelectedProducts ({ productCode, forceRemove = false }): Promise<any> {
    const currentSelectedProducts = state.currentSelectedProducts
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
    state.currentSelectedProducts = productList
    await currentSelectedProductsPremiumOnly()
  }

  async function resetoCurrentSelectedProducts (): Promise<any> {
    state.currentSelectedProducts = []
    await currentSelectedProductsPremiumOnly()
  }

  // set product with subscriptionStatus active to selected product
  async function setSubscribedProducts (): Promise<any> {
    const productList = state.productList
    let currentSelectedProducts = []
    currentSelectedProducts = productList.filter(product => product.subscriptionStatus === ProductStatus.ACTIVE).map((prod) => (prod.code))
    state.currentSelectedProducts = currentSelectedProducts
  }

  async function currentSelectedProductsPremiumOnly (): Promise<any> {
    const currentSelectedProducts = state.currentSelectedProducts
    const productList = state.productList

    let isPremiumOnly = false
    if (currentSelectedProducts.length > 0) {
      isPremiumOnly = productList.some(product => product.premiumOnly && currentSelectedProducts.includes(product.code))
    }
    state.isCurrentSelectedProductsPremiumOnly = isPremiumOnly
    return isPremiumOnly
  }

  async function fetchCurrentOrganizationGLInfo (accountId: number): Promise<any> {
    const response = await PaymentService.getRevenueAccountDetails(accountId)
    if (response?.data?.revenueAccount) {
      const revenueAccount = response?.data?.revenueAccount
      const result = {
        client: revenueAccount.client,
        responsibilityCentre: revenueAccount.responsibilityCentre,
        serviceLine: revenueAccount.serviceLine,
        stob: revenueAccount.stob,
        projectCode: revenueAccount.projectCode
      } as GLInfo
      setCurrentOrganizationGLInfo(result)
      return result
    }
    const result = {} as GLInfo
    setCurrentOrganizationGLInfo(result)
    return result
  }

  async function fetchOrgProductFeeCodes (): Promise<OrgProductFeeCode[]> {
    const response = await PaymentService.getOrgProductFeeCodes()
    if (response?.data?.codes && response?.data?.codes.length !== 0) {
      const unfilteredOrgProductFeeCodes = response.data.codes
      const result = unfilteredOrgProductFeeCodes.filter((orgProductFeeCode: OrgProductFeeCode) => {
        const code = orgProductFeeCode.code
        if (code.startsWith(FeeCodes.PPR_CHANGE_OR_AMENDMENT)) {
          return orgProductFeeCode
        }
      })
      state.orgProductFeeCodes = result
      return result
    }
    state.orgProductFeeCodes = []
    return []
  }

  async function createAccountFees (accoundId:number): Promise<any> {
    const accountFeePayload = JSON.parse(JSON.stringify(state.currentAccountFees))
    await PaymentService.createAccountFees(accoundId.toString(), { accountFees: accountFeePayload })
  }

  async function updateAccountFees (accountFee): Promise<any> {
    const { accoundId, accountFees } = accountFee
    const response = await PaymentService.updateAccountFees(accoundId.toString(), accountFees)
    if (response?.data && response.status === 200) {
      return response.data
    }
  }

  async function syncCurrentAccountFees (accoundId:number): Promise<AccountFee[]> {
    const response = await PaymentService.getAccountFees(accoundId.toString())
    if (response?.data && response.status === 200) {
      const result = response.data.accountFees
      setCurrentAccountFees(result)
      return result
    }
  }

  async function getOrgNameAutoComplete (searchValue: string): Promise<AutoCompleteResponse> {
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

  async function getOrgAdminContact (orgId: number): Promise<Address> {
    const response = await OrgService.getContactForOrg(orgId)
    return response
  }

  // Check if user has any accounts, if any, default the first returned value as the selected org.
  async function setCurrentOrganizationFromUserAccountSettings (): Promise<void> {
    const response = await UserService.getUserAccountSettings(userStore.userProfile?.keycloakGuid)
    if (response?.data) {
      // filter by account type and default first returned value as the current organization
      const orgs = response.data.filter(userSettings => (userSettings.type === 'ACCOUNT'))
      if (orgs?.length) {
        const orgId = +orgs[0].id
        // sync org and add to session
        await syncOrganization(orgId)
        await addOrgSettings(state.currentOrganization)
      }
    }
  }

  async function getOrgApiKeys (orgId) {
    const response = await OrgService.getOrgApiKeys(orgId)
    return response?.data || {}
  }

  async function revokeOrgApiKeys (ApiDetails) {
    const response = await OrgService.revokeOrgApiKeys(ApiDetails)
    return response?.data || {}
  }

  async function updateOrganizationAccessType ({ accessType, orgId = null, syncOrg = true }): Promise<boolean> {
    if (!orgId) orgId = state.currentOrganization?.id as number
    if (orgId && accessType) {
      try {
        const patchOrgPayload: PatchOrgPayload = {
          action: PatchActions.UPDATE_ACCESS_TYPE,
          accessType: accessType
        }
        const response = await OrgService.patchOrg(orgId, patchOrgPayload)
        if (response && response.status === 200 && syncOrg) {
          await syncOrganization(orgId)
        }
        return true
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('update Organization AccessType operation failed! - ', error)
        return false
      }
    }
  }

  return {
    ...toRefs(state),
    isPremiumAccount,
    needMissingBusinessDetailsRedirect,
    canEditBusinessInfo,
    isBusinessAccount,
    setAccessType,
    setMemberLoginOption,
    setGrantAccess,
    resetCurrentOrganisation,
    resetBcolDetails,
    setSelectedAccountType,
    setCurrentAccountSettings,
    resetInvitations,
    setCurrentOrganization,
    setCurrentMembership,
    setCurrentOrganizationAddress,
    setCurrentOrganizationName,
    setCurrentOrganizationPaymentType,
    setCurrentOrganizationType,
    setCurrentOrganizationPADInfo,
    setCurrentOrganizationGLInfo,
    setCurrentAccountFees,
    setResetAccountTypeOnSetupAccount,
    setViewOnlyMode,
    setCurrentOrganizationBusinessType,
    setCurrentOrganizationBcolProfile,
    resetCurrentOrganization,
    syncOrganization,
    suspendOrganization,
    syncMemberLoginOption,
    syncMembership,
    createOrgByStaff,
    updateLoginOption,
    createOrg,
    createGovmOrg,
    validatePADInfo,
    addOrgSettings,
    validateBcolAccount,
    isOrgNameAvailable,
    updateOrg,
    createInvitation,
    resendInvitation,
    deleteInvitation,
    validateInvitationToken,
    acceptInvitation,
    deactivateOrg,
    leaveTeam,
    updateMember,
    deleteUser,
    syncActiveOrgMembers,
    syncAddress,
    syncPendingOrgMembers,
    syncPendingOrgInvitations,
    addProductsToOrg,
    createUsers,
    resetPassword,
    getStatementsList,
    getStatement,
    fetchStatementSettings,
    updateStatementSettings,
    getStatementRecipients,
    updateStatementNotifications,
    getOrgPayments,
    getFailedInvoices,
    calculateFailedInvoices,
    resetAccountSetupProgress,
    resetAccountWhileSwitchingPremium,
    createAccountPayment,
    createTransaction,
    getInvoice,
    updateInvoicePaymentMethodAsCreditCard,
    downloadOBInvoice,
    getOrganizationForAffiliate,
    getOrgProducts,
    addOrgProducts,
    getProductList,
    addToCurrentSelectedProducts,
    resetoCurrentSelectedProducts,
    setSubscribedProducts,
    currentSelectedProductsPremiumOnly,
    fetchCurrentOrganizationGLInfo,
    fetchOrgProductFeeCodes,
    createAccountFees,
    updateAccountFees,
    syncCurrentAccountFees,
    getOrgNameAutoComplete,
    getOrgAdminContact,
    setCurrentOrganizationFromUserAccountSettings,
    getOrgApiKeys,
    revokeOrgApiKeys,
    updateOrganizationAccessType
  }
})
