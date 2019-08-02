import { Module, VuexModule, Mutation, Action } from 'vuex-module-decorators'
import loginServices from '@/services/login.services'
import { Business } from '@/models/business'
import { Contact } from '@/models/contact'
import businessServices from '@/services/business.services'

interface LoginPayload {
  businessNumber: string
  passCode: string
}

@Module({
  name: 'business'
})
export default class BusinessModule extends VuexModule {
  currentBusiness: Business = {
    businessIdentifier: ''
  }

  skippedContactEntry = false

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
    return businessServices.getBusiness(businessNumber)
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
  public async addContact (contact: Contact) {
    return businessServices.addContact(this.currentBusiness, contact)
      .then(response => {
        if ((response.status === 200 || response.status === 201) && response.data) {
          this.context.commit('setCurrentBusiness', response.data)
        }
      })
  }

  @Action({ rawError: true })
  public async updateContact (contact: Contact) {
    return businessServices.updateContact(this.currentBusiness, contact)
      .then(response => {
        if ((response.status === 200 || response.status === 201) && response.data) {
          this.context.commit('setCurrentBusiness', response.data)
        }
      })
  }
}
