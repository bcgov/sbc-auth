import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import {
  Business,
  BusinessRequest,
  FolioNumberload,
  LoginPayload,
  PasscodeResetLoad
} from '@/models/business'
import { CorpType, FilingTypes, LegalTypes, NrConditionalStates, NrState, SessionStorageKeys } from '@/util/constants'
import { CreateRequestBody as CreateAffiliationRequestBody, CreateNRAffiliationRequestBody } from '@/models/affiliation'
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

  public get businessAffiliations (): Business[] {
    return this.businesses
  }

  @Mutation
  public setCurrentBusiness (business: Business) {
    ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, business?.businessIdentifier)
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
      // Fetch and populate data for Name Request affiliations
      const affiliatedEntities = response.data.entities
      for (const entity of affiliatedEntities) {
        if (entity.corpType.code === CorpType.NAME_REQUEST) {
          await BusinessService.getNrData(entity.businessIdentifier)
            .then(response => {
              if (response?.status >= 200 && response?.status < 300 && response?.data) {
                // Keep the approved name in Sync, in the event of changes in Namex
                const approvedName = () => {
                  for (const nameItem of response.data.names) {
                    if ([NrState.APPROVED, NrState.CONDITION].includes(nameItem.state)) {
                      return nameItem.name
                    }
                  }
                }

                BusinessService.updateBusinessName({
                  businessIdentifier: entity.businessIdentifier,
                  name: approvedName()
                })

                const isIaEnabled = response.data.state === NrState.APPROVED ||
                    (response.data.state === NrState.CONDITIONAL &&
                    [NrConditionalStates.RECEIVED, NrConditionalStates.WAIVED].includes(response.data.consentFlag))

                entity.nameRequest = {
                  names: response.data.names,
                  id: response.data.id,
                  legalType: response.data.legalType,
                  nrNumber: response.data.nrNum,
                  state: response.data.state,
                  applicantEmail: response.data.applicants?.emailAddress,
                  applicantPhone: response.data.applicants?.phoneNumber,
                  enableIncorporation: isIaEnabled,
                  folioNumber: response.data.folioNumber,
                  target: response.data.target
                }
              }
            }).catch(err => {
              // eslint-disable-next-line no-console
              console.log(`Error fetching Name Request: ${err}`)
            })
        }
      }

      return affiliatedEntities
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
      await OrgService.removeAffiliation(orgId, businessNumber, undefined, false)
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
  public async createNamedBusiness (filingBody: BusinessRequest) {
    // Create an affiliation between implicit org and requested business
    const updateResponse = await BusinessService.createNamedBusiness(filingBody)
    if (updateResponse?.status >= 200 && updateResponse?.status < 300) {
      return updateResponse
    } else {
      // delete the created affiliation if the update failed for avoiding orphan records
      // unable to do these from backend, since it causes a circular dependency
      const orgId = filingBody?.filing?.header?.accountId
      const nrNumber = filingBody?.filing?.incorporationApplication?.nameRequest?.nrNumber
      await OrgService.removeAffiliation(orgId, nrNumber, undefined, false)
      return {
        errorMsg: 'Cannot add business due to some technical reasons'
      }
    }
  }

  // Following searchBusiness will search data from legal-api.
  @Action({ rawError: true })
  public async searchBusiness (businessNumber: string): Promise<any> {
    return BusinessService.searchBusiness(businessNumber)
      .then(response => {
        if (response.status === 200) {
          ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, businessNumber)
        }
      })
  }

  @Action({ rawError: true })
  public async createNumberedBusiness (accountId: number) {
    const filingBody: BusinessRequest = {
      filing: {
        header: {
          name: FilingTypes.INCORPORATION_APPLICATION,
          accountId: accountId
        },
        business: {
          legalType: LegalTypes.BCOMP
        },
        incorporationApplication: {
          nameRequest: {
            legalType: LegalTypes.BCOMP
          }
        }
      }
    }

    await BusinessService.createNumberedBusiness(filingBody)
      .then(response => {
        if (response && response.data && (response.status === 200 || response.status === 201)) {
          const tempRegNum = response.data.filing?.business?.identifier
          if (tempRegNum) {
            ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, tempRegNum)
            const redirectURL = `${ConfigHelper.getBusinessURL()}${tempRegNum}`

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
    // If the business is a new registration then remove the business filing from legal-db
    if (payload.business.corpType.code === CorpType.NEW_BUSINESS) {
      let filingResponse = await BusinessService.getFilings(payload.business.businessIdentifier)
      if (filingResponse && filingResponse.data && filingResponse.status === 200) {
        let filingId = filingResponse?.data?.filing?.header?.filingId
        // If there is a filing delete it which will delete the affiliation, else delete the affiliation
        if (filingId) {
          await BusinessService.deleteBusinessFiling(payload.business.businessIdentifier, filingId)
        } else {
          await OrgService.removeAffiliation(payload.orgIdentifier, payload.business.businessIdentifier, payload.passcodeResetEmail, payload.resetPasscode)
        }
      }
    } else {
      // Remove an affiliation between the given business and each specified org
      await OrgService.removeAffiliation(payload.orgIdentifier, payload.business.businessIdentifier, payload.passcodeResetEmail, payload.resetPasscode)
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

  @Action({ rawError: true })
  public async updateFolioNumber (folioNumberload: FolioNumberload) {
    await BusinessService.updateFolioNumber(folioNumberload)
  }

  @Action({ rawError: true })
  public async resetCurrentBusiness (): Promise<void> {
    this.context.commit('setCurrentBusiness', undefined)
    ConfigHelper.removeFromSession(SessionStorageKeys.BusinessIdentifierKey)
  }

  @Action({ rawError: true })
  public async resetBusinessPasscode (passCodeResetLoad: PasscodeResetLoad) {
    await BusinessService.resetBusinessPasscode(passCodeResetLoad)
  }
}
