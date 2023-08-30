import { Business, NameRequest } from '@/models/business'
import ConfigHelper from '@/util/config-helper'
import { SessionStorageKeys } from '@/util/constants'
import { appendAccountId } from 'sbc-common-components/src/util/common-util'

/** Navigation handler for entities dashboard. */
export const goToBusinessDashboard = async (business: Business): Promise<void> => {
  ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, business.businessIdentifier)
  let redirectURL = `${ConfigHelper.getBusinessURL()}${business.businessIdentifier}`
  window.location.href = appendAccountId(decodeURIComponent(redirectURL))
}

/** Navigation handler for Name Request application. */
export const goToNameRequest = async (nameRequest: NameRequest): Promise<void> => {
  await ConfigHelper.setNrCredentials(nameRequest)
  window.location.href = appendAccountId(`${ConfigHelper.getNameRequestUrl()}nr/${nameRequest.id}`)
}

/** Navigation handler for Societies Online */
export const goToSocieties = async (): Promise<void> => {
  window.open(appendAccountId(ConfigHelper.getSocietiesUrl()), '_blank')
}


/** Navigation handler for OneStop application */
export const goToOneStop = async (): Promise<void> => {
  window.location.href = appendAccountId(ConfigHelper.getOneStopUrl())
}

/** Navigation handler for Corporate Online application */
export const goToCorpOnline = async (): Promise<void> => {
  window.open(appendAccountId(ConfigHelper.getCorporateOnlineUrl()), '_blank')
}
