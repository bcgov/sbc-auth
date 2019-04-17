import Axios from 'axios'
const AUTHENTICATION_RESOURCE_NAME = '/authenticate'

export default {
  login (entityNumber, passCode) {
    return Axios.post(AUTHENTICATION_RESOURCE_NAME, { passcode: passCode, corp_num: entityNumber})
  }
}
