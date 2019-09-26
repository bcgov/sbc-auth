import Axios from 'axios'
import ConfigHelper from '../util/config-helper'
import { SessionStorageKeys } from '@/util/constants'

export default {
  login (entityNumber, passCode) {
    return Axios.post(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/token`, { username: entityNumber, password: passCode })
  },
  logout () {
    return Axios.post(`${ConfigHelper.getValue('VUE_APP_AUTH_ROOT_API')}/logout`, { refresh_token: ConfigHelper.getFromSession(SessionStorageKeys.KeyCloakRefreshToken) })
  }
}
