import { AccountType, GLCode, ProductCode } from '@/models/Staff'
import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import { MembershipType, OrgFilterParams, Organization } from '@/models/Organization'
import { AccountStatus } from '@/util/constants'
import { Address } from '@/models/address'
import { AffidavitInformation } from '@/models/affidavit'
import { Contact } from '@/models/contact'
import { Invitation } from '@/models/Invitation'
import InvitationService from '@/services/invitation.services'
import OrgService from '@/services/org.services'
import PaymentService from '@/services/payment.services'
import StaffService from '@/services/staff.services'
import { User } from '@/models/user'
import UserService from '@/services/user.services'

@Module({
  name: 'staff',
  namespaced: true
})
export default class StaffModule extends VuexModule {
  products: ProductCode[] = []
  accountTypes: AccountType[] = []
  activeStaffOrgs: Organization[] = []
  pendingStaffOrgs: Organization[] = []
  rejectedStaffOrgs: Organization[] = []
  pendingInvitationOrgs: Organization[] = []
  accountUnderReview: Organization
  accountUnderReviewAddress: Address
  accountUnderReviewAdmin: User
  accountUnderReviewAdminContact: Contact
  accountUnderReviewAffidavitInfo: AffidavitInformation

  public get accountNotaryName (): string {
    return this.accountUnderReviewAffidavitInfo?.issuer || '-'
  }

  public get accountNotaryContact (): Contact {
    return this.accountUnderReviewAffidavitInfo?.contacts?.length > 0 && this.accountUnderReviewAffidavitInfo?.contacts[0]
  }

  public get affidavitDocumentUrl (): string {
    return this.accountUnderReviewAffidavitInfo?.documentUrl
  }

  public get pendingReviewCount (): number {
    return this.pendingStaffOrgs?.length || 0
  }

  public get rejectedReviewCount (): number {
    return this.rejectedStaffOrgs?.length || 0
  }

  public get pendingInvitationsCount (): number {
    return this.pendingInvitationOrgs?.length || 0
  }

  @Mutation
  public setProducts (products: ProductCode[]) {
    this.products = products
  }

  @Mutation
  public setAccountTypes (accountType: AccountType[]) {
    this.accountTypes = accountType
  }

  @Mutation
  public setActiveStaffOrgs (activeOrgs: Organization[]) {
    this.activeStaffOrgs = activeOrgs
  }

  @Mutation
  public setPendingStaffOrgs (pendingOrgs: Organization[]) {
    this.pendingStaffOrgs = pendingOrgs
  }

  @Mutation
  public setRejectedStaffOrgs (rejectedOrgs: Organization[]) {
    this.rejectedStaffOrgs = rejectedOrgs
  }

  @Mutation
  public setPendingInvitationOrgs (pendingInvitationOrgs: Organization[]) {
    this.pendingInvitationOrgs = pendingInvitationOrgs
  }

  @Mutation
  public setAccountUnderReview (account: Organization) {
    this.accountUnderReview = account
  }

  @Mutation
  public setAccountUnderReviewAddress (address: Address) {
    this.accountUnderReviewAddress = address
  }

  @Mutation
  public setAccountUnderReviewAdmin (admin: User) {
    this.accountUnderReviewAdmin = admin
  }

  @Mutation
  public setAccountUnderReviewAffidavitInfo (affidavitInfo: AffidavitInformation) {
    this.accountUnderReviewAffidavitInfo = affidavitInfo
  }

  @Mutation
  public setAccountUnderReviewAdminContact (contact: Contact) {
    this.accountUnderReviewAdminContact = contact
  }

  @Action({ commit: 'setProducts', rawError: true })
  public async getProducts (): Promise<ProductCode[]> {
    const response = await StaffService.getProducts()
    if (response && response.data && response.status === 200) {
      return response.data
    }
  }

  @Action({ commit: 'setAccountTypes', rawError: true })
  public async getAccountTypes (): Promise<AccountType[]> {
    const response = await StaffService.getAccountTypes()
    if (response && response.data && response.status === 200) {
      return response.data
    }
  }

  @Action({ rawError: true })
  public async syncAccountUnderReview (organizationIdentifier: number): Promise<void> {
    const accountResponse = await OrgService.getOrganization(organizationIdentifier)
    if (accountResponse?.data && accountResponse?.status === 200) {
      this.context.commit('setAccountUnderReview', accountResponse.data)

      const addressResponse = await OrgService.getContactForOrg(organizationIdentifier)
      if (addressResponse) {
        this.context.commit('setAccountUnderReviewAddress', addressResponse)
      }

      const accountMembersResponse = await OrgService.getOrgMembers(organizationIdentifier, 'ACTIVE')
      if (accountMembersResponse?.data && accountMembersResponse?.status === 200) {
        const admin = accountMembersResponse.data.members.find(member => member.membershipTypeCode === MembershipType.Admin)?.user
        if (admin) {
          this.context.commit('setAccountUnderReviewAdmin', admin)
          const adminContactResponse = await UserService.getUserProfile(admin.username)
          if (adminContactResponse?.data && adminContactResponse?.status === 200) {
            const contact = adminContactResponse?.data?.contacts?.length > 0 && adminContactResponse?.data?.contacts[0]
            if (contact) {
              this.context.commit('setAccountUnderReviewAdminContact', contact)
            }
          }
        }
      }

      const affidavitResponse = await OrgService.getAffidavitInfo(organizationIdentifier)
      if (affidavitResponse?.data && affidavitResponse?.status === 200) {
        this.context.commit('setAccountUnderReviewAffidavitInfo', affidavitResponse.data)
      }
    }
  }

  @Action({ rawError: true })
  public async approveAccountUnderReview () {
    const orgId = this.context.state['accountUnderReview']?.id
    if (orgId) {
      await OrgService.approvePendingOrg(orgId)
      await this.context.dispatch('syncAccountUnderReview', orgId)
    }
  }

  @Action({ rawError: true })
  public async rejectAccountUnderReview () {
    const orgId = this.context.state['accountUnderReview']?.id
    if (orgId) {
      await OrgService.rejectPendingOrg(orgId)
      await this.context.dispatch('syncAccountUnderReview', orgId)
    }
  }

  @Action({ commit: 'setActiveStaffOrgs', rawError: true })
  public async syncActiveStaffOrgs () {
    const response = await StaffService.getStaffOrgs(AccountStatus.ACTIVE)
    return response?.data?.orgs || []
  }

  @Action({ commit: 'setPendingStaffOrgs', rawError: true })
  public async syncPendingStaffOrgs () {
    const response = await StaffService.getStaffOrgs(AccountStatus.PENDING_AFFIDAVIT_REVIEW)
    return response?.data?.orgs || []
  }

  @Action({ commit: 'setRejectedStaffOrgs', rawError: true })
  public async syncRejectedStaffOrgs () {
    const response = await StaffService.getStaffOrgs(AccountStatus.REJECTED)
    return response?.data?.orgs || []
  }

  @Action({ rawError: true })
  public async searchOrgs (filterParams: OrgFilterParams) {
    const response = await StaffService.searchOrgs(filterParams)
    if (response?.data) {
      return {
        limit: response.data.limit,
        page: response.data.page,
        total: response.data.total,
        orgs: response.data.orgs
      }
    }
    return {}
  }

  @Action({ commit: 'setPendingInvitationOrgs', rawError: true })
  public async syncPendingInvitationOrgs () {
    const response = await StaffService.getStaffOrgs(AccountStatus.PENDING_ACTIVATION)
    return response?.data?.orgs || []
  }

  @Action({ rawError: true })
  public async resendPendingOrgInvitation (invitation: Invitation) {
    return InvitationService.resendInvitation(invitation)
  }

  @Action({ rawError: true })
  public async deleteOrg (org: Organization) {
    const invResponse = await InvitationService.deleteInvitation(org.invitations[0].id)
    if (!invResponse || invResponse.status !== 200 || !invResponse.data) {
      throw Error('Unable to delete invitation')
    }
    const orgResponse = await OrgService.deactivateOrg(org.id)
    if (!orgResponse || orgResponse.status !== 204) {
      throw Error('Unable to delete org')
    }
  }

  @Action({ rawError: true })
  public async getGLCodeList () {
    const response = await PaymentService.getGLCodeList()
    return response?.data?.items || []
  }

  @Action({ rawError: true })
  public async getGLCodeFiling (distributionCodeId: string) {
    const response = await PaymentService.getGLCodeFiling(distributionCodeId)
    return response?.data?.items || []
  }

  @Action({ rawError: true })
  public async updateGLCodeFiling (glcodeFilingData: GLCode) {
    const response = await PaymentService.updateGLCodeFiling(glcodeFilingData)
    return response?.data || {}
  }
}
