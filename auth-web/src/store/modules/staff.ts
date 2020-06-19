import { AccountType, ProductCode } from '@/models/Staff'
import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import { AccountStatus } from '@/util/constants'
import { Organization } from '@/models/Organization'
import StaffService from '@/services/staff.services'

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
}
