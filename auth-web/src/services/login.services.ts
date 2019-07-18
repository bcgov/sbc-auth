import Axios from 'axios'
import ConfigHelper from '../util/config-helper'

export default {
  login (entityNumber, passCode) {
    return Axios.post(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/token`, { username: entityNumber, password: passCode })
  }
}
