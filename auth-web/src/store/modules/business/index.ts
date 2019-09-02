import { Module, VuexModule, Mutation, Action } from 'vuex-module-decorators'
import loginServices from '@/services/login.services'
import { Business } from '@/models/business'
import { Contact } from '@/models/contact'
import businessServices from '@/services/business.services'
import { Affiliation } from '@/models/affiliation'
import { Org } from '@/models/org'
import { RemoveBusinessPayload } from '@/models/Organization'

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

  currentOrg: Org = {
    name: ''
  }

  skippedContactEntry = false

  @Mutation
  public setCurrentBusiness (business: Business) {
    this.currentBusiness = business
  }

  @Mutation
  public setSkippedContactEntry (skippedStatus: boolean) {
    this.skippedContactEntry = skippedStatus
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
  public async addBusiness (payload: LoginPayload) {
    const affiliation: Affiliation = {
      businessIdentifier: payload.businessNumber,
      passCode: payload.passCode
    }

    // Create an implicit org for the current user and the requested business
    const createBusinessResponse = await businessServices.createOrg({ name: payload.businessNumber })

    // Create an affiliation between implicit org and requested business
    await businessServices.createAffiliation(createBusinessResponse.data['id'], affiliation)

    // Update store
    this.context.dispatch('getOrganizations', null, { root: true })
  }

  @Action({ rawError: true })
  public async removeBusiness (payload: RemoveBusinessPayload) {
    // Remove an affiliation between the given entity and org
    const removeAffiliationResponse = await businessServices.removeAffiliation(payload.orgIdentifier, payload.incorporationNumber)
    if (removeAffiliationResponse.status === 200) {
      // Update store
      this.context.dispatch('getOrganizations', null, { root: true })
    }
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
