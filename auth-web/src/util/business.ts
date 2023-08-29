import { AffiliationTypes, BusinessState, CorpTypes, LDFlags, NrDisplayStates, NrState } from '@/util/constants'
import { CorpTypeCd, GetCorpFullDescription } from '@bcrs-shared-components/corp-type-module'
import { Business } from '@/models/business'
import launchdarklyServices from 'sbc-common-components/src/services/launchdarkly.services'

/** Returns true if the affiliation is a Name Request.
 *
 * @param business
 */
export const isNameRequest = (business: Business): boolean => {
  return (business.corpType?.code === CorpTypes.NAME_REQUEST && !!business.nameRequest)
}

export const getEntityType = (item: Business): CorpTypes => {
  let entityType = item.corpType.code
  if (isNameRequest(item)) {
    entityType = item.nameRequest?.legalType
  }
  return entityType
}


/** Returns the temp business description. */
const _temporaryBusinessDescription = (business: Business): string => {
  switch ((business.corpType?.code || business.corpType) as CorpTypes) {
    case CorpTypes.INCORPORATION_APPLICATION:
      return AffiliationTypes.INCORPORATION_APPLICATION
    case CorpTypes.REGISTRATION:
      return AffiliationTypes.REGISTRATION
    default:
      return '' // should never happen
  }
}

export const getType = (business: Business): string => {
  if (isTemporaryBusiness(business) && CorpTypes.INCORPORATION_APPLICATION) {
    return _temporaryBusinessDescription(business)
  }
  if (isNameRequest(business)) {
    return AffiliationTypes.NAME_REQUEST
  }
  const code: unknown = business.corpType.code
  return GetCorpFullDescription(code as CorpTypeCd)
}

/**
 * Returns true if the affiliation is a temporary business.
 *
 * @param business
 */
export const isTemporaryBusiness = (business: Business): boolean => {
  return (
    (business.corpType?.code || business.corpType) === CorpTypes.INCORPORATION_APPLICATION ||
    (business.corpType?.code || business.corpType) === CorpTypes.REGISTRATION
  )
}

export const isSocieties = (item: Business): boolean => {
  const entityType = getEntityType(item)
  return (entityType === CorpTypes.CONT_IN_SOCIETY ||
    entityType === CorpTypes.SOCIETY ||
    entityType === CorpTypes.XPRO_SOCIETY)
}

export const isModernizedEntity = (item: Business): boolean => {
  const entityType = getEntityType(item)
  const supportedEntityFlags = launchdarklyServices.getFlag(LDFlags.IaSupportedEntities)?.split(' ') || []
  return supportedEntityFlags.includes(entityType)
}

export const isOtherEntities = (item: Business): boolean => {
  const entityType = getEntityType(item)
  return (entityType === CorpTypes.FINANCIAL ||
    entityType === CorpTypes.PRIVATE_ACT ||
    entityType === CorpTypes.PARISHES)
}

export const isForRestore = (item: Business): boolean => {
  const entityType = getEntityType(item)
  return (entityType === CorpTypes.BC_COMPANY ||
    entityType === CorpTypes.BC_CCC ||
    entityType === CorpTypes.BC_ULC_COMPANY ||
    entityType === CorpTypes.COOP ||
    entityType === CorpTypes.BENEFIT_COMPANY)
}

export const isColinEntity = (item: Business): boolean => {
  // todo: fixme
  const entityTpe = getEntityType(item)
  return [
    CorpTypes.CCC_CONTINUE_IN,
    CorpTypes.BC_CORPORATION,
    CorpTypes.ULC_CONTINUE_IN,
    CorpTypes.EXTRA_PRO_REG,
    CorpTypes.LL_PARTNERSHIP,
    CorpTypes.LIMITED_CO,
    CorpTypes.LIM_PARTNERSHIP,
    CorpTypes.BC_UNLIMITED,
    CorpTypes.XPRO_LL_PARTNR,
    CorpTypes.XPRO_LIM_PARTNR
  ].includes(entityTpe)
}

export const isSupportedRestorationEntities = (item: Business): boolean => {
  const entityType = getEntityType(item)
  const supportedEntityFlags = launchdarklyServices.getFlag(LDFlags.SupportRestorationEntities)?.split(' ') || []
  return supportedEntityFlags.includes(entityType)
}

/**
 * returns  NrState|BusinessState|NrDisplayStates|'Unknown' or string ...
 * @param business
 */
export const entityStatus = (business: Business): string => {
  if (isTemporaryBusiness(business)) {
    return BusinessState.DRAFT
  }
  if (isNameRequest(business)) {
    // Format name request state value
    const state = NrState[(business.nameRequest.state)?.toUpperCase()]
    if (!state) return 'Unknown'
    if (state === NrState.APPROVED && (!business.nameRequest.expirationDate)) return NrDisplayStates.PROCESSING
    else if (business.corpType.code === CorpTypes.INCORPORATION_APPLICATION ||
      business.corpType.code === CorpTypes.REGISTRATION ||
      state === NrState.DRAFT) {
      return NrDisplayStates[NrState.HOLD]
    } else return NrDisplayStates[state] || 'Unknown'
  }
  if (business.status) {
    return business.status.charAt(0)?.toUpperCase() + business.status?.slice(1)?.toLowerCase()
  }
  return BusinessState.ACTIVE
}
