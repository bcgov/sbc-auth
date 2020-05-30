import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import { Business, FolioNumberload, LoginPayload, NumberedBusinessRequest, UpdateFilingBody } from '@/models/business'
import { CreateRequestBody as CreateAffiliationRequestBody, CreateNRAffiliationRequestBody } from '@/models/affiliation'
import { FilingTypes, LegalTypes, SessionStorageKeys } from '@/util/constants'
import { Organization, RemoveBusinessPayload } from '@/models/Organization'
import BusinessService from '@/services/business.services'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import OrgService from '@/services/org.services'

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
  public async syncBusinesses (): Promise<Business[]> {
    const organization = this.context.rootState.org.currentOrganization
    if (!organization) {
      return []
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
    return OrgService.createAffiliation(currentOrganization.id, requestBody)
  }

  @Action({ rawError: true })
  public async updateBusinessName (businessNumber: string) {
    try {
      const businessResponse = await BusinessService.searchBusiness(businessNumber)
      if ((businessResponse?.status === 200) && businessResponse?.data?.business?.legalName) {
        const updateBusinessResponse = await BusinessService.updateBusinessName({
          businessIdentifier: businessNumber,
          name: businessResponse.data.business.legalName
        })
        if (updateBusinessResponse?.status === 200) {
          return updateBusinessResponse
        }
      }
      throw Error('update failed')
    } catch (error) {
      // delete the created affiliation if the update failed for avoiding orphan records
      // unable to do these from backend, since it causes a circular dependency
      const orgId = this.context.rootState.org.currentOrganization?.id
      await OrgService.removeAffiliation(orgId, businessNumber)
      return {
        errorMsg: 'Cannot add business due to some technical reasons'
      }
    }
  }

  @Action({ rawError: true })
  public async addNameRequest (requestBody: CreateNRAffiliationRequestBody) {
    const currentOrganization: Organization = this.context.rootState.org.currentOrganization

    // Create an affiliation between implicit org and requested business
    return OrgService.createNRAffiliation(currentOrganization.id, requestBody)
  }

  @Action({ rawError: true })
  public async updateFiling (filingBody: UpdateFilingBody) {
    // Create an affiliation between implicit org and requested business
    const updateResponse = await BusinessService.updateFiling(filingBody)
    if (updateResponse?.status >= 200 && updateResponse?.status < 300) {
      return updateResponse
    } else {
      // delete the created affiliation if the update failed for avoiding orphan records
      // unable to do these from backend, since it causes a circular dependency
      const orgId = filingBody?.filing?.header?.accountId
      const nrNumber = filingBody?.filing?.incorporationApplication?.nameRequest?.nrNumber
      await OrgService.removeAffiliation(orgId, nrNumber)
      return {
        errorMsg: 'Cannot add business due to some technical reasons'
      }
    }
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
  public async createNumberedBusiness (accountId: number) {
    const requestBody: NumberedBusinessRequest = {
      filing: {
        header: {
          name: FilingTypes.INCORPORATION_APPLICATION,
          accountId: accountId
        },
        business: {
          legalType: LegalTypes.BCOMP
        }
      }
    }

    await BusinessService.createNumberedBusiness(requestBody)
      .then(response => {
        if (response && response.data && (response.status === 200 || response.status === 201)) {
          const tempRegNum = response.data.filing?.business?.identifier
          if (tempRegNum) {
            ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, tempRegNum)
            const redirectURL = `${ConfigHelper.getCoopsURL()}${tempRegNum}`

            window.location.href = decodeURIComponent(redirectURL)
          }
        }
      }).catch(error => {
        // eslint-disable-next-line no-console
        console.log(error) // ToDo: Handle error: Redirect back to Homeview? Feedback required here
      })
  }

  @Action({ rawError: true })
  public async removeBusiness (payload: RemoveBusinessPayload) {
    // Remove an affiliation between the given business and each specified org
    for (const orgId of payload.orgIdentifiers) {
      await OrgService.removeAffiliation(orgId, payload.businessIdentifier)
    }
    await this.syncBusinesses()
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

  @Action({ rawError: true })
  public async updateFolioNumber (folioNumberload: FolioNumberload) {
    await BusinessService.updateFolioNumber(folioNumberload)
  }
}
