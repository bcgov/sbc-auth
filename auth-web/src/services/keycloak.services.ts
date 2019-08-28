import Keycloak from 'keycloak-js'
import configHelper from '../util/config-helper'
import { UserInfo } from '../models/userInfo'
import { SessionStorageKeys, AppConstants } from '../util/constants'

const kc: Keycloak.KeycloakInstance = null
const keyCloakConfig = `/${process.env.VUE_APP_PATH}/config/kc/keycloak.json`

export default {

  init (idpHint : string) {
    this.cleanupSession()
    let token = configHelper.getFromSession(SessionStorageKeys.KeyCloakToken)
    this.kc = Keycloak(keyCloakConfig)
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
      lastName: token.lastname,
      firstName: token.firstname,
      email: token.email,
      roles: token.realm_access.roles,
      keycloakGuid: token.jti,
      userName: token.username
    }
  },

  logout (redirectUrl: string) {
    let token = configHelper.getFromSession(SessionStorageKeys.KeyCloakToken)
    if (token) {
      this.kc = Keycloak(keyCloakConfig)
      this.kc.init({ token: token, onLoad: 'check-sso' }).success(authenticated => {
        if (authenticated) {
          configHelper.clearSession()
          if (!redirectUrl) {
            redirectUrl = window.location.origin + AppConstants.RootPath
          }
          this.kc.logout({ redirectUri: redirectUrl })
        }
      })
    }
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
