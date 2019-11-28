import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import { Business, LoginPayload } from '@/models/business'
import { Organization, RemoveBusinessPayload } from '@/models/Organization'
import { Affiliation } from '@/models/affiliation'
import BusinessService from '@/services/business.services'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import LoginService from '@/services/login.services'

import { SessionStorageKeys } from '@/util/constants'

@Module({
  name: 'business',
  namespaced: true
})
export default class BusinessModule extends VuexModule {
  currentBusiness: Business = undefined

  @Mutation
  public setCurrentBusiness (business: Business) {
    ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, business.businessIdentifier)
    this.currentBusiness = business
  }

  @Action({ commit: 'setCurrentBusiness', rawError: true })
  public async loadBusiness () {
    const businessIdentifier = ConfigHelper.getFromSession(SessionStorageKeys.BusinessIdentifierKey)
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

    const myOrg: Organization = this.context.rootGetters['org/myOrg']

    // Create an affiliation between implicit org and requested business
    await BusinessService.createAffiliation(myOrg.id, affiliation)

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
    for await (const orgId of payload.orgIdentifiers) {
      await BusinessService.removeAffiliation(orgId, payload.businessIdentifier)
    }
    this.context.dispatch('org/syncOrganizations', null, { root: true })
  }

  @Action({ commit: 'setCurrentBusiness', rawError: true })
  public async saveContact (contact: Contact) {
    let currentBusiness: Business = this.context.state['currentBusiness']
    let response = null
    if (!currentBusiness.contacts || currentBusiness.contacts.length === 0) {
      response = await BusinessService.addContact(currentBusiness, contact)
    } else {
      response = await BusinessService.updateContact(currentBusiness, contact)
    }
    if (response && response.data && (response.status === 200 || response.status === 201)) {
      return response.data
    }
  }
}
