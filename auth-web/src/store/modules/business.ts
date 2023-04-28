import { Action, Module, Mutation, VuexModule } from 'vuex-module-decorators'
import { AffiliationResponse, CreateRequestBody as CreateAffiliationRequestBody, CreateNRAffiliationRequestBody } from '@/models/affiliation'
import { BNRequest, RequestTracker, ResubmitBNRequest } from '@/models/request-tracker'
import { Business, BusinessRequest, FolioNumberload, LearBusiness, LoginPayload, NameRequest, PasscodeResetLoad } from '@/models/business'
import {
  CorpTypes,
  FilingTypes,
  LDFlags,
  LearFilingTypes,
  NrConditionalStates,
  NrEntityType,
  NrState,
  NrTargetTypes,
  SessionStorageKeys
} from '@/util/constants'
import { Organization, RemoveBusinessPayload } from '@/models/Organization'
import BusinessService from '@/services/business.services'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import { NameRequestResponse } from './../../models/affiliation'
import OrgService from '@/services/org.services'

@Module({
  name: 'business',
  namespaced: true
})
export default class BusinessModule extends VuexModule {
  currentBusiness: Business = undefined
  businesses: Business[] = []

  private get currentOrganization (): Organization {
    return this.context.rootState.org.currentOrganization
  }

  @Mutation
  public setCurrentBusiness (business: Business) {
    ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, business?.businessIdentifier)
    this.currentBusiness = business
  }

  @Mutation
  public setBusinesses (businesses: Business[]) {
    this.businesses = [...businesses]
  }

  /** This is the function that fetches and updates data for all NRs. */
  @Action({ rawError: true })
  public async syncBusinesses (): Promise<void> {
    const enableBcCccUlc = LaunchDarklyService.getFlag(LDFlags.EnableBcCccUlc) || false

    /** Returns True if NR is approved. */
    const isApproved = (nr: NameRequestResponse): boolean => (nr.stateCd === NrState.APPROVED)

    /** Returns True if NR is conditionally approved. NB: consent flag=null means "not required". */
    const isConditionallyApproved = (nr: NameRequestResponse): boolean => (
      nr.stateCd === NrState.CONDITIONAL && (
        nr.consentFlag === null ||
        nr.consentFlag === NrConditionalStates.RECEIVED ||
        nr.consentFlag === NrConditionalStates.WAIVED
      )
    )

    /** Returns True if NR is approved for incorporation. */
    const isApprovedForIa = (nr: NameRequestResponse): boolean => (
      (isApproved(nr) || isConditionallyApproved(nr)) &&
      nr.actions?.some(action => action.filingName === LearFilingTypes.INCORPORATION)
    )

    /** Returns True if NR is approved for registration. */
    const isApprovedForRegistration = (nr: NameRequestResponse): boolean => (
      (isApproved(nr) || isConditionallyApproved(nr)) &&
      nr.actions?.some(action => action.filingName === LearFilingTypes.REGISTRATION)
    )

    /** Returns True if NR has applicants for registration. */
    const isApplicantsExist = (nr: NameRequestResponse): boolean => {
      return nr.applicants && nr.applicants.length > 0
    }

    /** Returns target conditionally. */
    const getTarget = (nr: NameRequestResponse): NrTargetTypes => {
      const bcCorpTypes = [CorpTypes.BC_CCC, CorpTypes.BC_COMPANY, CorpTypes.BC_ULC_COMPANY]
      if (bcCorpTypes.includes(nr.legalType)) {
        // if FF is enabled then route to LEAR, else route to COLIN
        return enableBcCccUlc ? NrTargetTypes.LEAR : NrTargetTypes.COLIN
      }
      return nr.target
    }

    // initialize store
    this.setBusinesses([])

    // get current organization
    if (!this.currentOrganization) {
      console.log('Invalid organization') // eslint-disable-line no-console
      return
    }

    // get affiliated entities for this organization
    const entityResponse: AffiliationResponse[] = await OrgService.getAffiliatiatedEntities(this.currentOrganization.id)
      .then(response => {
        if (response?.data?.entities && response?.status === 200) {
          return response.data.entities
        }
        throw Error(`Invalid response = ${response}`)
      })
      .catch(error => {
        console.log('Error getting affiliated entities:', error) // eslint-disable-line no-console
        return [] as []
      })

    let affiliatedEntities: Business[] = []

    entityResponse.forEach((resp, i) => {
      const entity: Business = {
        businessIdentifier: resp.identifier,
        ...(resp.businessNumber && { businessNumber: resp.businessNumber }),
        ...(resp.legalName && { name: resp.legalName }),
        ...(resp.contacts && { contacts: resp.contacts }),
        ...((resp.draftType || resp.legalType) && { corpType: { code: resp.draftType || resp.legalType } }),
        ...(resp.legalType && { corpSubType: { code: resp.legalType } }),
        ...(resp.folioNumber && { folioNumber: resp.folioNumber }),
        ...(resp.lastModified && { lastModified: resp.lastModified }),
        ...(resp.modified && { modified: resp.modified }),
        ...(resp.modifiedBy && { modifiedBy: resp.modifiedBy }),
        ...(resp.nrNumber && { nrNumber: resp.nrNumber }),
        ...(resp.adminFreeze !== undefined ? { adminFreeze: resp.adminFreeze } : { adminFreeze: false }),
        ...(resp.goodStanding !== undefined ? { goodStanding: resp.goodStanding } : { goodStanding: true })
      }
      if (resp.nameRequest) {
        const nr = resp.nameRequest
        if (!entity.nrNumber && nr.nrNum) {
          entity.nrNumber = entity.nrNumber || nr.nrNum
        }
        entity.nameRequest = {
          actions: nr.actions,
          names: nr.names,
          id: nr.id,
          legalType: nr.legalType,
          nrNumber: nr.nrNum,
          state: nr.stateCd,
          applicantEmail: isApplicantsExist(nr) ? nr.applicants[0].emailAddress : null,
          applicantPhone: isApplicantsExist(nr) ? nr.applicants[0].phoneNumber : null,
          enableIncorporation: isApprovedForIa(nr) || isApprovedForRegistration(nr),
          folioNumber: nr.folioNumber,
          target: getTarget(nr),
          entityTypeCd: nr.entityTypeCd,
          natureOfBusiness: nr.natureBusinessInfo,
          expirationDate: nr.expirationDate,
          applicants: nr.applicants
        }
      }
      affiliatedEntities.push(entity)
    })
    // update store with initial results
    this.setBusinesses(affiliatedEntities)
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
      certifiedByName: payload.certifiedByName,
      passCode: payload.passCode
    }

    // Create an affiliation between implicit org and requested business
    return OrgService.createAffiliation(this.currentOrganization.id, requestBody)
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
      await OrgService.removeAffiliation(this.currentOrganization.id, businessNumber, undefined, false)
      return {
        errorMsg: 'Cannot add business due to some technical reasons'
      }
    }
  }

  @Action({ rawError: true })
  public async addNameRequest (requestBody: CreateNRAffiliationRequestBody) {
    // Create an affiliation between implicit org and requested business
    return OrgService.createNRAffiliation(this.currentOrganization.id, requestBody)
  }

  private addBusinessTypeforSP (filingBody: BusinessRequest, business: Business) {
    // add in Business Type for SP
    if (business.nameRequest.legalType === CorpTypes.SOLE_PROP) {
      if (business.nameRequest.entityTypeCd === NrEntityType.FR) {
        filingBody.filing.registration.businessType = CorpTypes.SOLE_PROP
      } else if (business.nameRequest.entityTypeCd === NrEntityType.DBA) {
        filingBody.filing.registration.businessType = NrEntityType.DBA
      }
    }
  }

  @Action({ rawError: true })
  public async createNamedBusiness ({ filingType, business }: { filingType: FilingTypes, business: Business}) {
    let filingBody: BusinessRequest = null

    switch (filingType) {
      case FilingTypes.INCORPORATION_APPLICATION: {
        filingBody = {
          filing: {
            business: {
              legalType: business.nameRequest.legalType
            },
            header: {
              accountId: this.currentOrganization.id,
              name: filingType
            },
            incorporationApplication: {
              nameRequest: {
                legalType: business.nameRequest.legalType,
                nrNumber: business.businessIdentifier || business.nameRequest.nrNumber
              }
            }
          }
        }

        // add in Business Type for SP
        this.addBusinessTypeforSP(filingBody, business)
        break
      }

      case FilingTypes.REGISTRATION: {
        filingBody = {
          filing: {
            header: {
              accountId: this.currentOrganization.id,
              name: filingType
            },
            registration: {
              business: {
                natureOfBusiness: business.nameRequest.natureOfBusiness
              },
              nameRequest: {
                legalType: business.nameRequest.legalType,
                nrNumber: business.nameRequest.nrNumber
              }
            }
          }
        }

        // add in Business Type for SP
        this.addBusinessTypeforSP(filingBody, business)
        break
      }
    }

    // create an affiliation between implicit org and requested business
    const response = await BusinessService.createDraftFiling(filingBody)
    if (response?.status >= 200 && response?.status < 300) {
      return response
    }

    // delete the created affiliation if the update failed for avoiding orphan records
    // unable to do this from backend, since it causes a circular dependency
    const orgIdentifier = this.currentOrganization.id
    const incorporationNumber = business.businessIdentifier
    await OrgService.removeAffiliation(orgIdentifier, incorporationNumber, undefined, false)

    return { errorMsg: 'Cannot add business due to some technical reasons' }
  }

  // Following searchBusiness will search data from legal-api.
  @Action({ rawError: true })
  public async searchBusiness (businessIdentifier: string): Promise<LearBusiness> {
    const response = await BusinessService.searchBusiness(businessIdentifier).catch(() => null)
    if (response?.status === 200 && response?.data?.business?.legalName) {
      ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, businessIdentifier)
      return response.data.business
    } else {
      throw Error('search failed')
    }
  }

  @Action({ rawError: true })
  public async createBNRequest (request: BNRequest): Promise<any> {
    return BusinessService.createBNRequest(request)
  }

  @Action({ rawError: true })
  public async getBNRequests (businessIdentifier: string): Promise<RequestTracker[]> {
    const response = await BusinessService.getBNRequests(businessIdentifier).catch(() => null)
    if (response?.status === 200) {
      return response.data.requestTrackers
    }
    return []
  }

  @Action({ rawError: true })
  public async resubmitBNRequest (resubmitRequest: ResubmitBNRequest): Promise<any> {
    const response = await BusinessService.resubmitBNRequest(resubmitRequest).catch(() => null)
    return response?.status === 200
  }

  @Action({ rawError: true })
  public async getRequestTracker (requestTrackerId: number): Promise<RequestTracker> {
    const response = await BusinessService.getRequestTracker(requestTrackerId).catch(() => null)
    if (response?.status === 200) {
      return response.data
    }
    return null
  }

  @Action({ rawError: true })
  public async createNumberedBusiness ({ filingType, business }): Promise<void> {
    const filingBody: BusinessRequest = {
      filing: {
        business: {
          legalType: business.nameRequest.legalType
        },
        header: {
          accountId: this.currentOrganization.id,
          name: filingType
        },
        incorporationApplication: {
          nameRequest: {
            legalType: business.nameRequest.legalType
          }
        }
      }
    }

    try {
      // create an affiliation between implicit org and requested business
      const response = await BusinessService.createDraftFiling(filingBody)
      if (!response?.data) throw Error('Invalid response data')
      if (response.status !== 200 && response.status !== 201) throw Error('Invalid response status')

      const tempRegNum = response.data.filing?.business?.identifier
      if (!tempRegNum) throw Error('Invalid temporary registration number')

      // redirect to Filings UI
      ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, tempRegNum)
      const redirectURL = `${ConfigHelper.getBusinessURL()}${tempRegNum}`
      window.location.href = decodeURIComponent(redirectURL)
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log(error) // ToDo: Handle error: Redirect back to Homeview? Feedback required here
    }
  }

  @Action({ rawError: true })
  public async removeBusiness (payload: RemoveBusinessPayload) {
    // If the business is a new registration then remove the business filing from legal-db
    if (payload.business.corpType.code === CorpTypes.INCORPORATION_APPLICATION) {
      let filingResponse = await BusinessService.getFilings(payload.business.businessIdentifier)
      if (filingResponse && filingResponse.data && filingResponse.status === 200) {
        let filingId = filingResponse?.data?.filing?.header?.filingId
        // If there is a filing delete it which will delete the affiliation, else delete the affiliation
        if (filingId) {
          await BusinessService.deleteBusinessFiling(payload.business.businessIdentifier, filingId)
        } else {
          const businessIdentifier = payload.business.businessIdentifier || payload.business.nameRequest.nrNumber
          await OrgService.removeAffiliation(payload.orgIdentifier, businessIdentifier, payload.passcodeResetEmail, payload.resetPasscode)
        }
      }
    } else {
      // Remove an affiliation between the given business and each specified org
      const businessIdentifier = payload.business.businessIdentifier || payload.business.nameRequest.nrNumber
      await OrgService.removeAffiliation(payload.orgIdentifier, businessIdentifier, payload.passcodeResetEmail, payload.resetPasscode)
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
  public resetCurrentBusiness (): void {
    this.context.commit('setCurrentBusiness', undefined)
    ConfigHelper.removeFromSession(SessionStorageKeys.BusinessIdentifierKey)
  }

  @Action({ rawError: true })
  public async resetBusinessPasscode (passCodeResetLoad: PasscodeResetLoad) {
    await BusinessService.resetBusinessPasscode(passCodeResetLoad)
  }
}
