import { Account, PaymentTypes, SessionStorageKeys } from '@/util/constants'

import CommonUtils from './common-util'
import { NameRequest } from '@/models/business'

export default class ConfigHelper {
  static async fetchConfig () {
    // fas-ui needs the following keys
    sessionStorage.setItem(SessionStorageKeys.PayApiUrl, ConfigHelper.getPayAPIURL())
    // sbc common components need the following keys
    sessionStorage.setItem(SessionStorageKeys.AuthApiUrl, ConfigHelper.getAuthAPIUrl())
    sessionStorage.setItem(SessionStorageKeys.StatusApiUrl, ConfigHelper.getStatusAPIUrl())
    sessionStorage.setItem(SessionStorageKeys.AuthWebUrl, ConfigHelper.getSelfURL())
    sessionStorage.setItem(SessionStorageKeys.FasWebUrl, ConfigHelper.getFasWebUrl())
    sessionStorage.setItem(SessionStorageKeys.RegistryHomeUrl, ConfigHelper.getRegistryHomeURL())
    sessionStorage.setItem(SessionStorageKeys.NameRequestUrl, ConfigHelper.getNameRequestUrl())
    sessionStorage.setItem(SessionStorageKeys.PprWebUrl, ConfigHelper.getPPRWebUrl())
    if (ConfigHelper.getSiteminderLogoutUrl()) {
      sessionStorage.setItem(SessionStorageKeys.SiteminderLogoutUrl, ConfigHelper.getSiteminderLogoutUrl())
    }
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
    return `${import.meta.env.VUE_APP_DASHBOARD_URL}`
  }

  static getRegistryHomeURL () {
    return `${import.meta.env.VUE_APP_REGISTRY_HOME_URL}`
  }

  static getBcrosDashboardURL () {
    return `${import.meta.env.VUE_APP_REGISTRY_HOME_URL}dashboard`
  }

  static getBcrosURL () {
    return `${ConfigHelper.getSelfURL()}/signin/bcros/`
  }

  static getSelfURL () {
    // this is without a trailing slash
    return `${window.location.origin}${import.meta.env.VUE_APP_PATH}`.replace(/\/$/, '') // remove the slash at the end
  }

  static getDirectorSearchURL () {
    return `${import.meta.env.VUE_APP_DIRECTOR_SEARCH_URL}`
  }

  static getNewBusinessURL () {
    // returns new business URL
    return `${import.meta.env.VUE_APP_BUSINESS_CREATE_URL}`
  }

  static getFileServerUrl () {
    return `${import.meta.env.VUE_APP_FILE_SERVER_URL}`
  }

  static getNroUrl () {
    return `${import.meta.env.VUE_APP_NRO_URL}`
  }

  static getNameRequestUrl () {
    return `${import.meta.env.VUE_APP_NAME_REQUEST_URL}`
  }

  static getBceIdOsdLink () {
    return `${import.meta.env.VUE_APP_BCEID_OSD_LINK}`
  }

  static getAffidavitSize () {
    return `${import.meta.env.VUE_APP_AFFIDAVIT_FILE_SIZE}`
  }

  static getPayAPIURL () {
    return `${import.meta.env.VUE_APP_PAY_API_URL}` + `${import.meta.env.VUE_APP_PAY_API_VERSION}`
  }

  static getPaymentPayeeName () {
    return `${import.meta.env.VUE_APP_PAYMENT_PAYEE_NAME}` || 'BC Registries and Online Services'
  }

  static getAuthAPIUrl () {
    return `${import.meta.env.VUE_APP_AUTH_API_URL}` + `${import.meta.env.VUE_APP_AUTH_API_VERSION}`
  }

  static getAuthResetAPIUrl () {
    return `${import.meta.env.VUE_APP_AUTH_API_URL}` + '/test/reset'
  }

  static getLegalAPIUrl () {
    return `${import.meta.env.VUE_APP_LEGAL_API_URL}` + `${import.meta.env.VUE_APP_LEGAL_API_VERSION}`
  }

  static getLegalAPIV2Url () {
    return `${import.meta.env.VUE_APP_LEGAL_API_URL}` + `${import.meta.env.VUE_APP_LEGAL_API_VERSION_2}`
  }

  static getVonAPIUrl () {
    return `${import.meta.env.VUE_APP_VON_API_URL}` + `${import.meta.env.VUE_APP_VON_API_VERSION}`
  }

  static getStatusAPIUrl () {
    return `${import.meta.env.VUE_APP_STATUS_API_URL}` + `${import.meta.env.VUE_APP_STATUS_API_VERSION}`
  }

  static getEntitySelectorUrl () {
    return `${import.meta.env.VUE_APP_ENTITY_SELECTOR_URL}`
  }

  static getOneStopUrl () {
    return `${import.meta.env.VUE_APP_ONE_STOP_URL}`
  }

  static getCorporateOnlineUrl () {
    return `${import.meta.env.VUE_APP_CORPORATE_ONLINE_URL}`
  }

  static getSocietiesUrl () {
    return `${process.env.VUE_APP_SOCIETIES_URL}`
  }

  static getCorpFormsUrl () {
    return `${process.env.VUE_APP_CORP_FORMS_URL}`
  }

  static getFasWebUrl () {
    return `${import.meta.env.VUE_APP_FAS_WEB_URL}`
  }

  static getPPRWebUrl () {
    return `${import.meta.env.VUE_APP_PPR_WEB_URL}`
  }

  static getSiteminderLogoutUrl () {
    return `${import.meta.env.VUE_APP_SITEMINDER_LOGOUT_URL}`
  }

  static apiDocumentationUrl () {
    return `${import.meta.env.VUE_APP_API_DOCUMENTATION_URL}`
  }

  static getRegistrySearchUrl () {
    return `${import.meta.env.VUE_APP_REGISTRY_SEARCH_URL}`
  }

  static getHotjarId () {
    return `${import.meta.env.VUE_APP_HOTJAR_ID}`
  }

  static getLdClientId () {
    return `${import.meta.env.VUE_APP_AUTH_LD_CLIENT_ID}`
  }

  static getSentryDsn () {
    return `${import.meta.env.VUE_APP_SENTRY_DSN}`
  }

  static getAddressCompleteKey () {
    return `${import.meta.env.VUE_APP_ADDRESS_COMPLETE_KEY}`
  }

  static getAccountApprovalSlaInDays () {
    return `${import.meta.env.VUE_APP_APPROVE_ACCOUNT_SLA_DAYS}` || '5'
  }

  static getKeycloakAuthUrl () {
    return `${import.meta.env.VUE_APP_KEYCLOAK_AUTH_URL}`
  }

  static getKeycloakRealm () {
    return `${import.meta.env.VUE_APP_KEYCLOAK_REALM}`
  }

  static getKeycloakClientId () {
    return `${import.meta.env.VUE_APP_KEYCLOAK_CLIENTID}`
  }

  static getNotifiyAPIUrl () {
    return `${import.meta.env.VUE_APP_NOTIFY_API_URL}` + `${import.meta.env.VUE_APP_NOTIFY_API_VERSION}`
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

  // Allowed redirect back to same page URUI list
  static getAllowedUrlForRedirectToSamePage (): any {
    return [
      CommonUtils.trimTrailingSlashURL(ConfigHelper.getRegistryHomeURL()),
      CommonUtils.trimTrailingSlashURL(ConfigHelper.getNameRequestUrl()),
      CommonUtils.trimTrailingSlashURL(ConfigHelper.getPPRWebUrl())
    ]
  }
}
