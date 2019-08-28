import Axios from 'axios'
import { SessionStorageKeys } from './constants'

/**
 * the configs are used since process.env doesnt play well when we hae only one build config and multiple deployments..so going for this
 */
const url = `/${process.env.VUE_APP_PATH}/config/configuration.json`
const KEYCLOAK_TOKEN_SESSION_KEY = 'KEYCLOAK_TOKEN'

export default {
  fetchConfig () {
    // console.log('New code:'+url)
    return Axios
      .get(url)
      .then(response => {
        sessionStorage.setItem(SessionStorageKeys.ApiConfigKey, JSON.stringify(response.data))
      }).catch(err => {
        throw err
      }
      )
  },

  /**
 * this will run everytime when vue is being loaded..so do the call only when session storage doesnt have the values
 */
  saveConfigToSessionStorage () {
    if (sessionStorage.getItem(SessionStorageKeys.ApiConfigKey)) {
      return Promise.resolve()
    } else {
      return this.fetchConfig()
    }
  },

  getValue (key: String) {
    // @ts-ignore
    return JSON.parse(sessionStorage.getItem(SessionStorageKeys.ApiConfigKey))[key]
  },

  addToSession (key:string, value:any) {
    sessionStorage.setItem(key, value)
  },

  getFromSession (key:string):string {
    return sessionStorage.getItem(key)
  },

  removeFromSession (key:string) {
    sessionStorage.removeItem(key)
  },

  clearSession () {
    sessionStorage.clear()
  }
}
