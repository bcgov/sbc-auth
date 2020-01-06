import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import { Business, LoginPayload } from '@/models/business'
import { Organization, RemoveBusinessPayload } from '@/models/Organization'
import BusinessService from '@/services/business.services'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import { CreateRequestBody as CreateAffiliationRequestBody } from '@/models/affiliation'
import OrgService from '@/services/org.services'
import { SessionStorageKeys } from '@/util/constants'

@Module({
  name: 'business',
  namespaced: true
})
export default class BusinessModule extends VuexModule {
  currentBusiness: Business = undefined
  businesses: Business[] = []

  @Mutation
  public setCurrentBusiness (business: Business) {
    ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, business.businessIdentifier)
    this.currentBusiness = business
  }

  @Mutation
  public setBusinesses (businesses: Business[]) {
    this.businesses = businesses
  }

  @Action({ commit: 'setBusinesses', rawError: true })
  public async syncBusinesses (organization?: Organization): Promise<Business[]> {
    if (!organization) {
      organization = this.context.rootState.org.currentOrganization
    }
    const response = await OrgService.getAffiliatiatedEntities(organization.id)
    if (response && response.data && response.status === 200) {
      return response.data.entities
    }
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
    const requestBody: CreateAffiliationRequestBody = {
      businessIdentifier: payload.businessIdentifier,
      passCode: payload.passCode
    }

    const currentOrganization: Organization = this.context.rootState.org.currentOrganization

    // Create an affiliation between implicit org and requested business
    await OrgService.createAffiliation(currentOrganization.id, requestBody)
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
    for (const orgId of payload.orgIdentifiers) {
      await OrgService.removeAffiliation(orgId, payload.businessIdentifier)
    }
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
