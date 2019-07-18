import Axios from 'axios'

/**
 * the configs are used since process.env doesnt play well when we hae only one build config and multiple deployments..so going for this
 */
let url = '/static/config/configuration.json'
export default {
  fetchConfig () {
    return Axios
      .get(url)
      .then(response => {
        sessionStorage.setItem('API_CONFIG', JSON.stringify(response.data))
      }).catch(err => {
        throw err
      }
      )
  },

  /**
 * this will run everytime when vue is being loaded..so do the call only when session storage doesnt have the values
 */
  saveConfigToSessionStorage () {
    if (sessionStorage.getItem('API_CONFIG')) {
      return Promise.resolve()
    } else {
      return this.fetchConfig()
    }
  },

  getValue (key: String) {
    // @ts-ignore
    return JSON.parse(sessionStorage.getItem('API_CONFIG'))[key]
  }
}
