import Axios from 'axios'

/**
 * the configs are used since process.env doesnt play well when we hae only one build config and multiple deployments..so going for this
 */
const url = `/${process.env.VUE_APP_PATH}/config/configuration.json`
const SESSION_STORAGE_KEY = 'AUTH_API_CONFIG'
export default {
  fetchConfig () {
    console.log('New code:'+url)
    return Axios
      .get(url)
      .then(response => {
        sessionStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(response.data))
      }).catch(err => {
        throw err
      }
      )
  },

  /**
 * this will run everytime when vue is being loaded..so do the call only when session storage doesnt have the values
 */
  saveConfigToSessionStorage () {
    if (sessionStorage.getItem(SESSION_STORAGE_KEY)) {
      return Promise.resolve()
    } else {
      return this.fetchConfig()
    }
  },

  getValue (key: String) {
    // @ts-ignore
    return JSON.parse(sessionStorage.getItem(SESSION_STORAGE_KEY))[key]
  }
}
