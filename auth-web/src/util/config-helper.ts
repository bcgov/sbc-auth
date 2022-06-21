import { Account, PaymentTypes, SessionStorageKeys } from '@/util/constants'

import Axios from 'axios'
import CommonUtils from './common-util'
import { NameRequest } from '@/models/business'

/**
 * the configs are used since process.env doesnt play well when we hae only one build config and multiple deployments..so going for this
 */
const url = `${process.env.VUE_APP_PATH}config/configuration.json`

export default class ConfigHelper {
  static async fetchConfig () {
    const response = await Axios.get(url)
    sessionStorage.setItem(SessionStorageKeys.ApiConfigKey, JSON.stringify(response.data))
    // sbc common components need the following keys
    sessionStorage.setItem(SessionStorageKeys.AuthApiUrl, ConfigHelper.getAuthAPIUrl())
    sessionStorage.setItem(SessionStorageKeys.StatusApiUrl, ConfigHelper.getStatusAPIUrl())
    sessionStorage.setItem(SessionStorageKeys.AuthWebUrl, ConfigHelper.getSelfURL())
    sessionStorage.setItem(SessionStorageKeys.FasWebUrl, ConfigHelper.getFasWebUrl())
    sessionStorage.setItem(SessionStorageKeys.RegistryHomeUrl, ConfigHelper.getRegistryHomeURL())
    sessionStorage.setItem(SessionStorageKeys.NameRequestUrl, ConfigHelper.getNameRequestUrl())
    sessionStorage.setItem(SessionStorageKeys.PprWebUrl, ConfigHelper.getPPRWebUrl())
    sessionStorage.setItem(SessionStorageKeys.SiteminderLogoutUrl, ConfigHelper.getSiteminderLogoutUrl())
  }

  /**
 * this will run everytime when vue is being loaded..so do the call only when session storage doesnt have the values
 */
  static saveConfigToSessionStorage () {
    // Commenting the cache code to initiate the value on every load.
    // if (sessionStorage.getItem(SessionStorageKeys.ApiConfigKey)) {
    //   return Promise.resolve()
    // } else {
    return this.fetchConfig()
    // }
  }

  static getBusinessURL () {
    // this needs trailing slash
    return `${window.location.origin}/business/`
  }

  static getRegistryHomeURL () {
    return `${ConfigHelper.getValue('REGISTRY_HOME_URL')}`
  }

  static getBcrosDashboardURL () {
    return `${ConfigHelper.getValue('REGISTRY_HOME_URL')}dashboard`
  }

  static getBcrosURL () {
    return `${ConfigHelper.getSelfURL()}/signin/bcros/`
  }

  static getSelfURL () {
    // this is without a trailing slash
    return `${window.location.origin}${process.env.VUE_APP_PATH}`.replace(/\/$/, '') // remove the slash at the end
  }

  static getDirectorSearchURL () {
    return ConfigHelper.getValue('DIRECTOR_SEARCH_URL')
  }

  static getNewBusinessURL () {
    // returns new business URL
    return ConfigHelper.getValue('BUSINESS_CREATE_URL')
  }

  static getFileServerUrl () {
    return ConfigHelper.getValue('FILE_SERVER_URL')
  }

  static getNroUrl () {
    return ConfigHelper.getValue('NRO_URL')
  }

  static getNameRequestUrl () {
    return ConfigHelper.getValue('NAME_REQUEST_URL')
  }

  static getBceIdOsdLink () {
    return ConfigHelper.getValue('BCEID_URL')
  }

  static getAffidavitSize () {
    return ConfigHelper.getValue('AFFIDAVIT_FILE_SIZE')
  }

  static getPayAPIURL () {
    return ConfigHelper.getValue('PAY_API_URL') + ConfigHelper.getValue('PAY_API_VERSION')
  }

  static getPaymentPayeeName () {
    return ConfigHelper.getValue('PAYMENT_PAYEE_NAME') || 'BC Registries and Online Services'
  }

  static getAuthAPIUrl () {
    return ConfigHelper.getValue('AUTH_API_URL') + ConfigHelper.getValue('AUTH_API_VERSION')
  }

  static getAuthResetAPIUrl () {
    return ConfigHelper.getValue('AUTH_API_URL') + '/test/reset'
  }

  static getLegalAPIUrl () {
    return ConfigHelper.getValue('LEGAL_API_URL') + ConfigHelper.getValue('LEGAL_API_VERSION')
  }

  static getVonAPIUrl () {
    return ConfigHelper.getValue('VON_API_URL') + ConfigHelper.getValue('VON_API_VERSION')
  }

  static getStatusAPIUrl () {
    return ConfigHelper.getValue('STATUS_API_URL') + ConfigHelper.getValue('STATUS_API_VERSION')
  }

  static getEntitySelectorUrl () {
    return ConfigHelper.getValue('ENTITY_SELECTOR_URL')
  }

  static getOneStopUrl () {
    return ConfigHelper.getValue('ONE_STOP_URL')
  }

  static getCorporateOnlineUrl () {
    return ConfigHelper.getValue('CORPORATE_ONLINE_URL')
  }

  static getFasWebUrl () {
    return ConfigHelper.getValue('FAS_WEB_URL')
  }

  static getPPRWebUrl () {
    return ConfigHelper.getValue('PPR_WEB_URL')
  }

  static getSiteminderLogoutUrl () {
    return ConfigHelper.getValue('SITEMINDER_LOGOUT_URL')
  }

  static apiDocumentationUrl () {
    return ConfigHelper.getValue('API_DOCUMENTATION_URL')
  }

  static getValue (key: String) {
    // @ts-ignore
    return JSON.parse(sessionStorage.getItem(SessionStorageKeys.ApiConfigKey))[key]
  }

  static addToSession (key:string, value:any) {
    sessionStorage.setItem(key, value)
  }

  static getFromSession (key:string):string {
    return sessionStorage.getItem(key)
  }

  static removeFromSession (key:string) {
    sessionStorage.removeItem(key)
  }

  static clearSession () {
    sessionStorage.clear()
  }

  static accountSettingsRoute () {
    return `/account/${JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.CurrentAccount) || '{}').id || 0}/settings`
  }

  static paymentsAllowedPerAccountType () {
    return {
      [Account.BASIC]: [ PaymentTypes.CREDIT_CARD, PaymentTypes.ONLINE_BANKING ],
      [Account.PREMIUM]: [ PaymentTypes.PAD, PaymentTypes.BCOL ],
      [Account.UNLINKED_PREMIUM]: [ PaymentTypes.PAD, PaymentTypes.BCOL ]
    }
  }

  static async setNrCredentials (nameRequest: NameRequest) {
    // Set name request applicant info to retrieve on redirect
    sessionStorage.setItem('BCREG-nrNum', nameRequest.nrNumber)
    sessionStorage.setItem('BCREG-emailAddress', nameRequest.applicantEmail)
    sessionStorage.setItem('BCREG-phoneNumber', nameRequest.applicantPhone)
  }
  static getAccountApprovalSlaInDays () {
    return ConfigHelper.getValue('APPROVE_ACCOUNT_SLA_DAYS') || '5'
  }

  // Allowed redirect back to same page URUI list
  static getAllowedUrlForRedirectToSamePage (): any {
    return [
      CommonUtils.trimTrailingSlashURL(ConfigHelper.getRegistryHomeURL()),
      CommonUtils.trimTrailingSlashURL(ConfigHelper.getNameRequestUrl()),
      CommonUtils.trimTrailingSlashURL(ConfigHelper.getPPRWebUrl())
    ]
  }
}
