import Axios from 'axios'
const AUTHENTICATION_RESOURCE_NAME = '/auth/api/token'

export default {
  login (entityNumber, passCode) {
    return Axios.post(AUTHENTICATION_RESOURCE_NAME, { username: entityNumber, password: passCode })
  }
}
