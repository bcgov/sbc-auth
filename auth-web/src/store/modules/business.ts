import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import { Business, LoginPayload } from '@/models/business'
import { Affiliation } from '@/models/affiliation'
import BusinessService from '@/services/business.services'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import LoginService from '@/services/login.services'
import { RemoveBusinessPayload } from '@/models/Organization'
import { SessionStorageKeys } from '@/util/constants'

@Module({
  name: 'business',
  namespaced: true
})
export default class BusinessModule extends VuexModule {
  currentBusiness: Business = {
    businessIdentifier: '',
    businessNumber: '',
    name: ''
  }

  @Mutation
  public setCurrentBusiness (business: Business) {
    this.currentBusiness = business
  }

  @Action({ rawError: true })
  public async login (payload: LoginPayload) {
    return LoginService.login(payload.businessIdentifier, payload.passCode)
  }

  @Action
  public async createBusinessIfNotFound (businessNumber: string) {
    return this.loadBusiness(businessNumber).catch(() => {
      BusinessService.createBusiness({ businessIdentifier: businessNumber })
        .then(createResponse => {
          if ((createResponse.status === 200 || createResponse.status === 201) && createResponse.data) {
            this.context.commit('setCurrentBusiness', createResponse.data)
          }
        })
    })
  }

  @Action({ commit: 'setCurrentBusiness', rawError: true })
  public async loadBusiness (businessIdentifier: string) {
    const response = await BusinessService.getBusiness(businessIdentifier)
    if (response && response.data && response.status === 200) {
      return response.data
    }
  }

  @Action({ rawError: true })
  public async addBusiness (payload: LoginPayload) {
    const affiliation: Affiliation = {
      businessIdentifier: payload.businessIdentifier,
      passCode: payload.passCode
    }

    // Create an implicit org for the current user and the requested business
    const createBusinessResponse = await BusinessService.createOrg({
      name: payload.businessIdentifier
    })

    // Create an affiliation between implicit org and requested business
    await BusinessService.createAffiliation(createBusinessResponse.data.id, affiliation)

    // Update store
    this.context.dispatch('org/syncOrganizations', null, { root: true })
  }

  // Following searchBusiness will search data from legal-api.
  @Action({ rawError: true })
  public async searchBusiness (businessNumber: string) {
    return BusinessService.searchBusiness(businessNumber)
      .then(response => {
        if (response.status === 200) {
          ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, businessNumber)
        }
      })
  }

  @Action({ rawError: true })
  public async removeBusiness (payload: RemoveBusinessPayload) {
    // Remove an affiliation between the given business and each specified org
    try {
      for await (const orgId of payload.orgIdentifiers) {
        await BusinessService.removeAffiliation(orgId, payload.businessIdentifier)
      }
    } catch (exception) {

    } finally {
      this.context.dispatch('org/syncOrganizations', null, { root: true })
    }
  }

  @Action({ commit: 'setCurrentBusiness', rawError: true })
  public async addContact (contact: Contact) {
    return BusinessService.addContact(this.currentBusiness, contact)
  }

  @Action({ commit: 'setCurrentBusiness', rawError: true })
  public async updateContact (contact: Contact) {
    return BusinessService.updateContact(this.currentBusiness, contact)
  }
}
