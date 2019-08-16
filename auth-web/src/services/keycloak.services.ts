import Keycloak from 'keycloak-js'
import configHelper from '../util/config-helper'
import { UserInfo } from '../models/userInfo'
import { SessionStorageKeys } from '../util/constants'

const kc: Keycloak.KeycloakInstance = null

export default {

  init (idpHint : string) {
    this.cleanupSession()
    let token = configHelper.getFromSession(SessionStorageKeys.KeyCloakToken)
    this.kc = Keycloak(`/${process.env.VUE_APP_PATH}/config/keycloak.json`)
    let kcLogin = this.kc.login
    this.kc.login = (options) => {
      options.idpHint = idpHint
      kcLogin(options)
    }

    return this.kc.init({ token: token, onLoad: 'login-required' })
  },

  initSessionStorage () {
    configHelper.addToSession(SessionStorageKeys.KeyCloakToken, this.kc.token)
    configHelper.addToSession(SessionStorageKeys.KeyCloakRefreshToken, this.kc.refreshToken)
  },

  getUserInfo () : UserInfo {
    let token = this.kc.tokenParsed
    return {
      familyName: token.family_name,
      givenName: token.given_name,
      email: token.email,
      roles: token.realm_access.roles,
      keycloakGuid: token.jti,
      userName: token.username
    }
  },

  login (idpHint:string) {
    this.kc.login({ idpHint: idpHint })
  },

  cleanupSession () {
    configHelper.removeFromSession(SessionStorageKeys.KeyCloakToken)
    configHelper.removeFromSession(SessionStorageKeys.KeyCloakRefreshToken)
  },

  refreshToken () {
    this.kc.updateToken().success(refreshed => {
      if (refreshed) {
        this.addToSession()
      }
    }).error(() => {
      this.cleanupSession()
    })
  }

}
