import Axios from 'axios'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import { SessionStorageKeys } from './constants'

/**
 * the configs are used since process.env doesnt play well when we hae only one build config and multiple deployments..so going for this
 */
const url = `${process.env.VUE_APP_PATH}config/configuration.json`

export default class ConfigHelper {
  static async fetchConfig () {
    const response = await Axios.get(url)
    sessionStorage.setItem(SessionStorageKeys.ApiConfigKey, JSON.stringify(response.data))
  }

  /**
 * this will run everytime when vue is being loaded..so do the call only when session storage doesnt have the values
 */
  static saveConfigToSessionStorage () {
    if (sessionStorage.getItem(SessionStorageKeys.ApiConfigKey)) {
      return Promise.resolve()
    } else {
      return this.fetchConfig()
    }
  }

  static getCoopsURL () {
    // this needs trailing slash
    return `${window.location.origin}/${process.env.VUE_APP_PATH_COOPS}/`
  }

  static getBcrosURL () {
    return `${ConfigHelper.getSelfURL()}/signin/bcros/`
  }

  static getNewBusinessURL () {
    // returns new business URL
    return ConfigHelper.getValue('VUE_APP_PATH_NEW_BUSINESS')
  }

  static getSelfURL () {
    // this is without a trailing slash
    return `${window.location.origin}${process.env.VUE_APP_PATH}`.replace(/\/$/, '') // remove the slash at the end
  }

  static getPayAPIURL () {
    return ConfigHelper.getValue('VUE_APP_PAY_ROOT_API')
  }

  static getBceIdOsdLink () {
    return ConfigHelper.getValue('BCEID_OSD_LINK')
  }

  static getAffidavitSize () {
    return ConfigHelper.getValue('AFFIDAVIT_FILE_SIZE')
  }

  static getAuthAPIUrl () {
    return ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')
  }

  static getFileServerUrl () {
    return ConfigHelper.getValue('FILE_SERVER_URL')
  }

  static getAuthResetAPIUrl () {
    return ConfigHelper.getValue('VUE_APP_AUTH_RESET_API')
  }

  static getSearchApplicationUrl () {
    return ConfigHelper.getValue('DIRECTOR_SEARCH_URL')
  }

  static getLegalAPIUrl () {
    return ConfigHelper.getValue('VUE_APP_LEGAL_ROOT_API')
  }

  static getNroUrl () {
    return ConfigHelper.getValue('NRO_URL')
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
}
