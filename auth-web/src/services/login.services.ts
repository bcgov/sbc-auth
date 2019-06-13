import Axios from 'axios'
const AUTHENTICATION_RESOURCE_NAME = 'token'

export default {
  login (entityNumber, passCode) {
    return Axios.post(process.env.VUE_APP_ROOT_API + AUTHENTICATION_RESOURCE_NAME, { username: entityNumber, password: passCode })
  }
}
