import { AccountType, ProductCode } from '@/models/Staff'
import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import StaffService from '@/services/staff.services'

@Module({
  name: 'staff',
  namespaced: true
})
export default class StaffModule extends VuexModule {
  products: ProductCode[] = []
  accountTypes: AccountType[] = []

  @Mutation
  public setProducts (products: ProductCode[]) {
    this.products = products
  }

  @Mutation
  public setAccountTypes (accountType: AccountType[]) {
    this.accountTypes = accountType
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
}
