import Keycloak from 'keycloak-js'
import configHelper from '../util/config-helper'
import { UserInfo } from '../models/userInfo'
import { SessionStorageKeys } from '../util/constants'

const kc: Keycloak.KeycloakInstance = null
const keyCloakConfig = `/${process.env.VUE_APP_PATH}/config/kc/keycloak.json`
const parsedToken = null

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

  initSession () {
    configHelper.addToSession(SessionStorageKeys.KeyCloakToken, this.kc.token)
    configHelper.addToSession(SessionStorageKeys.KeyCloakRefreshToken, this.kc.refreshToken)
    this.parsedToken = this.kc.tokenParsed
  },

  getUserInfo () : UserInfo {
    if (!this.parsedToken) {
      this.parsedToken = this.decodeToken()
    }
    return {
      lastName: this.parsedToken.lastname,
      firstName: this.parsedToken.firstname,
      email: this.parsedToken.email,
      roles: this.parsedToken.realm_access.roles,
      keycloakGuid: this.parsedToken.jti,
      userName: this.parsedToken.username
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
            redirectUrl = window.location.origin + process.env.VUE_APP_PATH
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
    // Set the token expiry time as the minValidity to force refresh token
    let tokenExpiresIn = this.kc.tokenParsed['exp'] - Math.ceil(new Date().getTime() / 1000) + this.kc.timeSkew + 100
    this.kc.updateToken(tokenExpiresIn).success((refreshed) => {
      if (refreshed) {
        this.initSession()
      }
    }).error(() => {
      this.cleanupSession()
    })
  },

  verifyRoles (allowedRoles:[], disabledRoles:[]) {
    let isAuthorized = false
    if (allowedRoles || disabledRoles) {
      let userInfo = this.getUserInfo()
      isAuthorized = allowedRoles ? allowedRoles.some(role => userInfo.roles.includes(role)) : !disabledRoles.some(role => userInfo.roles.includes(role))
    } else {
      isAuthorized = true
    }
    return isAuthorized
  },

  decodeToken () {
    try {
      let token = sessionStorage.getItem(SessionStorageKeys.KeyCloakToken)
      const base64Url = token.split('.')[1]
      const base64 = decodeURIComponent(window.atob(base64Url).split('').map(function (c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
      }).join(''))
      return JSON.parse(base64)
    } catch (error) {
      throw new Error('Error parsing JWT - ' + error)
    }
  }

}
