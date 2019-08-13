import Keycloak from 'keycloak-js'
import configHelper from '../util/config-helper'
import { UserInfo } from '../models/userInfo'

const kc: Keycloak.KeycloakInstance = null

export default {

  init () {
    this.cleanupSession()
    let token = configHelper.getFromSession('KEYCLOAK_TOKEN')
    this.kc = Keycloak(`/${process.env.VUE_APP_PATH}/config/keycloak.json`)
    return this.kc.init({ token: token, onLoad: 'check-sso' })
  },

  initSessionStorage () {
    configHelper.addToSession('KEYCLOAK_TOKEN', this.kc.token)
    configHelper.addToSession('KEYCLOAK_REFRESH', this.kc.refreshToken)
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
    configHelper.removeFromSession('KEYCLOAK_TOKEN')
    configHelper.removeFromSession('KEYCLOAK_REFRESH')
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
