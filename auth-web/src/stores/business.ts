import {
  AffiliationInvitationStatus,
  AffiliationInvitationType,
  CorpTypes,
  LDFlags,
  LearFilingTypes,
  NrConditionalStates,
  NrEntityType,
  NrState,
  NrTargetTypes,
  SessionStorageKeys
} from '@/util/constants'
import {
  AffiliationResponse,
  AlternateNames,
  CreateRequestBody as CreateAffiliationRequestBody,
  CreateNRAffiliationRequestBody,
  NameRequestResponse
} from '@/models/affiliation'
import { AmalgamationTypes, FilingTypes } from '@bcrs-shared-components/enums'
import { BNRequest, RequestTracker, ResubmitBNRequest } from '@/models/request-tracker'
import { Business, BusinessRequest, CorpType, FolioNumberload, LearBusiness, LoginPayload,
  PasscodeResetLoad } from '@/models/business'
import { Organization, RemoveBusinessPayload } from '@/models/Organization'
import { computed, reactive, toRefs } from '@vue/composition-api'
import AffiliationInvitationService from '@/services/affiliation-invitation.services'
import BusinessService from '@/services/business.services'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import OrgService from '@/services/org.services'
import { defineStore } from 'pinia'
import { useOrgStore } from './org'

export const useBusinessStore = defineStore('business', () => {
  const state = reactive({
    currentBusiness: undefined as Business,
    businesses: [] as Business[],
    removeExistingAffiliationInvitation: false
  })

  function $reset () {
    state.currentBusiness = undefined
    state.businesses = []
  }

  // Grabs from Org store.
  const currentOrganization = computed<Organization>(() => {
    return useOrgStore().currentOrganization
  })

  function determineDisplayName (
    legalName: string,
    legalType: CorpTypes,
    identifier: string,
    alternateNames: AlternateNames[]
  ): string {
    if (!LaunchDarklyService.getFlag(LDFlags.AlternateNamesMbr, false)) {
      return legalName
    }
    if ([CorpTypes.SOLE_PROP, CorpTypes.PARTNERSHIP].includes(legalType)) {
      // Intentionally show blank, if the alternate name is not found. This is to avoid showing the legal name.
      return alternateNames?.find(alt => alt.identifier === identifier)?.operatingName
    } else {
      return legalName
    }
  }

  /* Internal function to build the business object. */
  function buildBusinessObject (resp: AffiliationResponse): Business {
    return {
      businessIdentifier: resp.identifier,
      ...(resp.businessNumber && { businessNumber: resp.businessNumber }),
      ...(resp.legalName &&
          { name: determineDisplayName(resp.legalName, resp.legalType, resp.identifier, resp.alternateNames) }),
      ...(resp.contacts && { contacts: resp.contacts }),
      ...((resp.draftType || resp.legalType) && { corpType: { code: resp.draftType || resp.legalType } }),
      ...(resp.legalType && { corpSubType: { code: resp.legalType } }),
      ...(resp.folioNumber && { folioNumber: resp.folioNumber }),
      ...(resp.lastModified && { lastModified: resp.lastModified }),
      ...(resp.modified && { modified: resp.modified }),
      ...(resp.modifiedBy && { modifiedBy: resp.modifiedBy }),
      ...(resp.nrNumber && { nrNumber: resp.nrNumber }),
      ...(resp.adminFreeze !== undefined ? { adminFreeze: resp.adminFreeze } : { adminFreeze: false }),
      ...(resp.goodStanding !== undefined ? { goodStanding: resp.goodStanding } : { goodStanding: true }),
      ...(resp.state && { status: resp.state })
    }
  }

  /* Internal function to build the namerequest object. */
  function buildNameRequestObject (nr: NameRequestResponse) {
    const enableBcCccUlc = LaunchDarklyService.getFlag(LDFlags.EnableBcCccUlc) || false

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

    /** Returns True if NR is conditionally approved. NB: consent flag=null means "not required". */
    const isConditionallyApproved = (nr: NameRequestResponse): boolean => (
      nr.stateCd === NrState.CONDITIONAL && (
        nr.consentFlag === null ||
        nr.consentFlag === NrConditionalStates.RECEIVED ||
        nr.consentFlag === NrConditionalStates.WAIVED
      )
    )

    /** Returns True if NR is approved. */
    const isApproved = (nr: NameRequestResponse): boolean => (nr.stateCd === NrState.APPROVED)

    /** Returns True if NR is approved for incorporation or registration. */
    const isApprovedForIaOrRegistration = (nr: NameRequestResponse): boolean => (
      (isApproved(nr) || isConditionallyApproved(nr)) &&
      (nr.actions?.some(action => action.filingName === LearFilingTypes.INCORPORATION) ||
      nr.actions?.some(action => action.filingName === LearFilingTypes.REGISTRATION))
    )

    return {
      actions: nr.actions,
      names: nr.names,
      id: nr.id,
      legalType: nr.legalType,
      nrNumber: nr.nrNum,
      state: nr.stateCd,
      applicantEmail: isApplicantsExist(nr) ? nr.applicants[0].emailAddress : null,
      applicantPhone: isApplicantsExist(nr) ? nr.applicants[0].phoneNumber : null,
      enableIncorporation: isApprovedForIaOrRegistration(nr),
      folioNumber: nr.folioNumber,
      target: getTarget(nr),
      entityTypeCd: nr.entityTypeCd,
      requestTypeCd: nr.requestTypeCd,
      requestActionCd: nr.requestActionCd,
      natureOfBusiness: nr.natureBusinessInfo,
      expirationDate: nr.expirationDate,
      applicants: nr.applicants,
      corpNum: nr.corpNum
    }
  }

  /* Internal function for sorting affiliations / entities by invites. */
  function sortEntitiesByInvites (affiliatedEntities: Business[]): Business[] {
    // bubble the ones with the invitations to the top
    affiliatedEntities?.sort((a, b) => {
      if (a.affiliationInvites && !b.affiliationInvites) {
        return -1
      }
      if (!a.affiliationInvites && b.affiliationInvites) {
        return 1
      }
      return 0
    })
    return affiliatedEntities
  }

  async function handleAffiliationInvitations (affiliatedEntities: Business[]): Promise<Business[]> {
    if (!LaunchDarklyService.getFlag(LDFlags.AffiliationInvitationRequestAccess)) {
      return affiliatedEntities
    }

    const pendingAffiliationInvitations = await AffiliationInvitationService.getAffiliationInvitations(currentOrganization.value.id) || []
    const includeAffiliationInviteRequest = LaunchDarklyService.getFlag(LDFlags.EnableAffiliationDelegation) || false

    for (const affiliationInvite of pendingAffiliationInvitations) {
      // Skip over affiliation requests for type REQUEST for now.
      if (affiliationInvite.type === AffiliationInvitationType.REQUEST && !includeAffiliationInviteRequest) {
        continue
      }
      const isFromOrg = affiliationInvite.fromOrg.id === currentOrganization.value.id
      const isToOrgAndPending = affiliationInvite.toOrg?.id === currentOrganization.value.id &&
        affiliationInvite.status === AffiliationInvitationStatus.Pending
      const isAccepted = affiliationInvite.status === AffiliationInvitationStatus.Accepted
      const business = affiliatedEntities.find(
        business => business.businessIdentifier === affiliationInvite.entity.businessIdentifier)

      if (business && (isToOrgAndPending || isFromOrg)) {
        business.affiliationInvites = (business.affiliationInvites || []).concat([affiliationInvite])
      } else if (!business && isFromOrg && !isAccepted) {
        // This returns corpType: 'BEN' instead of corpType: { code: 'BEN' }.
        const corpType = affiliationInvite.entity.corpType
        const newBusiness = { ...affiliationInvite.entity,
          affiliationInvites: [affiliationInvite],
          corpType: { code: corpType as unknown as string } as CorpType }
        affiliatedEntities.push(newBusiness)
      }
    }

    return sortEntitiesByInvites(affiliatedEntities)
  }

  /** This is the function that fetches and updates data for all NRs. */
  async function syncBusinesses (): Promise<void> {
    state.businesses = []
    if (!currentOrganization.value) {
      console.log('Invalid organization') // eslint-disable-line no-console
      return
    }

    // get affiliated entities for this organization
    const entityResponse: AffiliationResponse[] = await OrgService.getAffiliatedEntities(currentOrganization.value.id)
    let affiliatedEntities: Business[] = []

    entityResponse.forEach((resp) => {
      const entity: Business = buildBusinessObject(resp)
      if (resp.nameRequest) {
        const nr = resp.nameRequest
        if (!entity.nrNumber && nr.nrNum) {
          entity.nrNumber = entity.nrNumber || nr.nrNum
        }
        entity.nameRequest = buildNameRequestObject(nr)
      }
      affiliatedEntities.push(entity)
    })

    affiliatedEntities = await handleAffiliationInvitations(affiliatedEntities)

    // update store with initial results
    state.businesses = [...affiliatedEntities]
  }

  async function loadBusiness () {
    const businessIdentifier = ConfigHelper.getFromSession(SessionStorageKeys.BusinessIdentifierKey)
    // Need to look at LEAR, because it has the up-to-date names.
    const learBusiness = await searchBusiness(businessIdentifier)
    const response = await BusinessService.getBusiness(businessIdentifier)
    if (response?.data && response.status === 200) {
      ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, response.data.businessIdentifier)
      const business = response.data
      business.name = determineDisplayName(
        learBusiness.legalName, learBusiness.legalType as CorpTypes, learBusiness.identifier, learBusiness.alternateNames)
      state.currentBusiness = business
      return response.data
    }
  }

  async function addBusiness (payload: LoginPayload) {
    const requestBody: CreateAffiliationRequestBody = {
      businessIdentifier: payload.businessIdentifier,
      certifiedByName: payload.certifiedByName,
      passCode: payload.passCode
    }

    // Create an affiliation between implicit org and requested business
    return OrgService.createAffiliation(currentOrganization.value.id, requestBody)
  }

  async function addNameRequest (requestBody: CreateNRAffiliationRequestBody) {
    // Create an affiliation between implicit org and requested business
    return OrgService.createNRAffiliation(currentOrganization.value.id, requestBody)
  }

  async function createNamedBusiness ({ filingType, business }: { filingType: FilingTypes, business: Business}) {
    let filingBody: BusinessRequest = null

    // add in Business Type for SP
    const addBusinessTypeforSP = (filingBody: BusinessRequest, business: Business): BusinessRequest => {
      if (business.nameRequest.entityTypeCd === NrEntityType.FR) {
        filingBody.filing.registration.businessType = CorpTypes.SOLE_PROP
      } else if (business.nameRequest.entityTypeCd === NrEntityType.DBA) {
        filingBody.filing.registration.businessType = NrEntityType.DBA
      }
      return filingBody
    }

    switch (filingType) {
      case FilingTypes.AMALGAMATION_APPLICATION: {
        filingBody = {
          filing: {
            business: {
              legalType: business.nameRequest.legalType
            },
            header: {
              accountId: currentOrganization.value.id,
              name: filingType
            },
            amalgamationApplication: {
              type: AmalgamationTypes.REGULAR,
              nameRequest: {
                legalType: business.nameRequest.legalType,
                nrNumber: business.businessIdentifier || business.nameRequest.nrNumber
              }
            }
          }
        }
        break
      }

      case FilingTypes.INCORPORATION_APPLICATION: {
        filingBody = {
          filing: {
            business: {
              legalType: business.nameRequest.legalType
            },
            header: {
              accountId: currentOrganization.value.id,
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
        if (business.nameRequest.legalType === CorpTypes.SOLE_PROP) {
          addBusinessTypeforSP(filingBody, business)
        }
        break
      }

      case FilingTypes.REGISTRATION: {
        filingBody = {
          filing: {
            business: {
              legalType: business.nameRequest.legalType
            },
            header: {
              accountId: currentOrganization.value.id,
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
        addBusinessTypeforSP(filingBody, business)
        break
      }

      case FilingTypes.CONTINUATION_IN: {
        filingBody = {
          filing: {
            business: {
              legalType: business.nameRequest.legalType
            },
            header: {
              accountId: currentOrganization.value.id,
              name: filingType
            },
            continuationIn: {
              nameRequest: {
                legalType: business.nameRequest.legalType,
                nrNumber: business.nameRequest.nrNumber
              }
            }
          }
        }
      }
    }

    // create an affiliation between implicit org and requested business
    const response = await BusinessService.createDraftFiling(filingBody)
    if (response?.status >= 200 && response?.status < 300) {
      return response
    }

    // delete the created affiliation if the update failed for avoiding orphan records
    // unable to do this from backend, since it causes a circular dependency
    const orgIdentifier = currentOrganization.value.id
    const incorporationNumber = business.businessIdentifier
    await OrgService.removeAffiliation(orgIdentifier, incorporationNumber, undefined, false)

    return { errorMsg: 'Cannot add business due to some technical reasons' }
  }

  // Following searchBusiness will search data from legal-api.
  async function searchBusiness (businessIdentifier: string): Promise<LearBusiness> {
    const response = await BusinessService.searchBusiness(businessIdentifier).catch(() => null)
    if (response?.status === 200 && response?.data?.business?.legalName) {
      ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, businessIdentifier)
      return response.data.business
    } else {
      throw Error('search failed')
    }
  }

  async function searchBusinessIndex (identifier: string): Promise<number> {
    return state.businesses.findIndex(business => business.businessIdentifier === identifier)
  }

  async function getBusinessNameByIdentifier (identifier: string): Promise<string | null> {
    const business = state.businesses.find(business => business.businessIdentifier === identifier)
    return business ? business.name : null
  }

  async function createBNRequest (request: BNRequest): Promise<any> {
    return BusinessService.createBNRequest(request)
  }

  async function searchNRIndex (identifier: string): number {
    return this.businesses.findIndex(business => business.nrNumber === identifier)
  }

  async function getBNRequests (businessIdentifier: string): Promise<RequestTracker[]> {
    const response = await BusinessService.getBNRequests(businessIdentifier).catch(() => null)
    if (response?.status === 200) {
      return response.data.requestTrackers
    }
    return []
  }

  async function downloadBusinessSummary (businessIdentifier: string): Promise<void> {
    await BusinessService.fetchBusinessSummary(businessIdentifier).catch(() => null)
  }

  async function resubmitBNRequest (resubmitRequest: ResubmitBNRequest): Promise<any> {
    const response = await BusinessService.resubmitBNRequest(resubmitRequest).catch(() => null)
    return response?.status === 200
  }

  async function getRequestTracker (requestTrackerId: number): Promise<RequestTracker> {
    const response = await BusinessService.getRequestTracker(requestTrackerId).catch(() => null)
    if (response?.status === 200) {
      return response.data
    }
    return null
  }

  function isAffiliated (identifier: string): boolean {
    return state.businesses.some(business => business.businessIdentifier === identifier)
  }

  function isAffiliatedNR (nrNum: string): boolean {
    return this.businesses.some(business => business.nrNumber === nrNum)
  }

  async function createNumberedBusiness ({ filingType, business }): Promise<void> {
    const filingBody: BusinessRequest = {
      filing: {
        business: {
          legalType: business.nameRequest.legalType
        },
        header: {
          accountId: currentOrganization.value.id,
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
      console.log(error)
      // ToDo: Handle error: Redirect back to Homeview? Feedback required here
    }
  }

  async function removeBusiness (payload: RemoveBusinessPayload) {
    // If the business is a new registration then remove the business filing from legal-db
    if ([CorpTypes.AMALGAMATION_APPLICATION,
      CorpTypes.INCORPORATION_APPLICATION,
      CorpTypes.CONTINUATION_IN,
      CorpTypes.REGISTRATION].includes(payload.business.corpType.code)) {
      const filingResponse = await BusinessService.getFilings(payload.business.businessIdentifier)
      if (filingResponse?.data && filingResponse.status === 200) {
        const filingId = filingResponse?.data?.filing?.header?.filingId
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

  async function saveContact (contact: Contact) {
    const currentBusiness: Business = state.currentBusiness
    let response = null
    if (!currentBusiness.contacts || currentBusiness.contacts.length === 0) {
      response = await BusinessService.addContact(currentBusiness, contact)
    } else {
      response = await BusinessService.updateContact(currentBusiness, contact)
    }
    if (response?.data && (response.status === 200 || response.status === 201)) {
      ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, response.data?.businessIdentifier)
      state.currentBusiness = response.data
      return response.data
    }
  }

  async function updateFolioNumber (folioNumberload: FolioNumberload) {
    await BusinessService.updateFolioNumber(folioNumberload)
  }

  function resetCurrentBusiness (): void {
    state.currentBusiness = undefined
    ConfigHelper.removeFromSession(SessionStorageKeys.BusinessIdentifierKey)
  }

  async function resetBusinessPasscode (passCodeResetLoad: PasscodeResetLoad) {
    await BusinessService.resetBusinessPasscode(passCodeResetLoad)
  }

  function setRemoveExistingAffiliationInvitation (value: boolean) {
    state.removeExistingAffiliationInvitation = value
  }

  return {
    ...toRefs(state),
    currentOrganization,
    syncBusinesses,
    loadBusiness,
    addBusiness,
    addNameRequest,
    createNamedBusiness,
    searchBusiness,
    searchBusinessIndex,
    getBusinessNameByIdentifier,
    createBNRequest,
    getBNRequests,
    downloadBusinessSummary,
    resubmitBNRequest,
    getRequestTracker,
    isAffiliated,
    isAffiliatedNR,
    createNumberedBusiness,
    removeBusiness,
    saveContact,
    updateFolioNumber,
    resetCurrentBusiness,
    resetBusinessPasscode,
    searchNRIndex,
    setRemoveExistingAffiliationInvitation,
    $reset
  }
})
