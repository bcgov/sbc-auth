import { Module, VuexModule, Mutation, Action } from 'vuex-module-decorators'
import loginServices from '@/services/login.services'
import store from '@/store'
import { Business } from '@/models/business'
import { Contact } from '@/models/contact'
import businessServices from '@/services/business.services'

interface LoginPayload {
  businessNumber: string
  passCode: string
}

@Module({
  dynamic: true,
  store,
  name: 'business',
  namespaced: true
})
export default class BusinessModule extends VuexModule {
  currentBusiness: Business = {
    businessIdentifier: ''
  }

  @Mutation
  public setCurrentBusiness (business: Business) {
    this.currentBusiness = business
  }

  @Action({ rawError: true })
  public async login (payload: LoginPayload) {
    return loginServices.login(payload.businessNumber, payload.passCode)
  }

  @Action
  public async loadBusiness (businessNumber: string) {
    businessServices.getBusiness(businessNumber)
      .then(response => {
        if (response.data) {
          this.context.commit('setCurrentBusiness', response.data)
        }
      })
      .catch(() => {
        businessServices.createBusiness({ businessIdentifier: businessNumber })
          .then(createResponse => {
            if ((createResponse.status === 200 || createResponse.status === 201) && createResponse.data) {
              this.context.commit('setCurrentBusiness', createResponse.data)
            }
          })
      })
  }

  @Action({ rawError: true })
  public async updateContact (contact: Contact) {
    const business = { ...this.currentBusiness, contact1: contact }
    return businessServices.updateBusiness(business)
  }
}
