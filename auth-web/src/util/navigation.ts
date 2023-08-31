import ConfigHelper from './config-helper'
import { NameRequest } from '@/models/business'
import { SessionStorageKeys } from './constants'
import { appendAccountId } from 'sbc-common-components/src/util/common-util'

/** Navigation handler for entities dashboard. */
export const goToDashboard = (businessIdentifier: string): void => {
  ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, businessIdentifier)
  const redirectURL = `${ConfigHelper.getBusinessURL()}${businessIdentifier}`
  window.location.href = appendAccountId(decodeURIComponent(redirectURL))
}

/** Navigation handler for Name Request application. */
export const goToNameRequest = (nameRequest: NameRequest): void => {
  ConfigHelper.setNrCredentials(nameRequest)
  window.location.href = appendAccountId(`${ConfigHelper.getNameRequestUrl()}nr/${nameRequest.id}`)
}

/** Navigation handler for OneStop application */
export const goToOneStop = (): void => {
  window.location.href = appendAccountId(ConfigHelper.getOneStopUrl())
}

/** Navigation handler for Corporate Online application */
export const goToCorpOnline = (): void => {
  window.open(appendAccountId(ConfigHelper.getCorporateOnlineUrl()), '_blank')
}

export const goToFormPage = (): void => {
  window.open(ConfigHelper.getCorpFormsUrl(), '_blank')
}

/** Navigation handler for Societies Online */
export const goToSocieties = (): void => {
  window.open(appendAccountId(ConfigHelper.getSocietiesUrl()), '_blank')
}
