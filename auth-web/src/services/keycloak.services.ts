import Keycloak, { KeycloakInitOptions, KeycloakInstance, KeycloakLoginOptions, KeycloakTokenParsed } from 'keycloak-js'
import { SessionStorageKeys } from '@/util/constants'
import { UserInfo } from '@/models/userInfo'
import configHelper from '@/util/config-helper'

const keyCloakConfig = `${process.env.VUE_APP_PATH}config/kc/keycloak.json`

interface UserToken extends KeycloakTokenParsed {
  lastname: string;
  firstname: string;
  email: string;
  // eslint-disable-next-line camelcase
  realm_access_roles: string[];
  jti: string;
  username: string;
}

class KeyCloakService {
  private kc: KeycloakInstance
  private parsedToken: any
  private static instance: KeyCloakService

  public static getInstance (): KeyCloakService {
    if (this.instance) {
      return this.instance
    }
    this.instance = new KeyCloakService()
    return this.instance
  }

  init (idpHint: string) {
    this.cleanupSession()
    const token = configHelper.getFromSession(SessionStorageKeys.KeyCloakToken)
    this.kc = Keycloak(keyCloakConfig)
    const kcLogin = this.kc.login
    this.kc.login = (options?: KeycloakLoginOptions) => {
      options.idpHint = idpHint
      return kcLogin(options)
    }
    return this.kc.init({ token: token, onLoad: 'login-required' })
  }

  initSession () {
    configHelper.addToSession(SessionStorageKeys.KeyCloakToken, this.kc.token)
    configHelper.addToSession(SessionStorageKeys.KeyCloakIdToken, this.kc.idToken)
    configHelper.addToSession(SessionStorageKeys.KeyCloakRefreshToken, this.kc.refreshToken)
    configHelper.addToSession(SessionStorageKeys.UserFullName, this.getUserInfo().fullName)
    this.parsedToken = this.kc.tokenParsed as UserToken
  }

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
      userName: this.parsedToken.username,
      fullName: `${this.parsedToken.firstname} ${this.parsedToken.lastname}`
    }
  }

  async logout (redirectUrl: string) {
    let token = configHelper.getFromSession(SessionStorageKeys.KeyCloakToken)
    if (token) {
      this.kc = Keycloak(keyCloakConfig)
      let kcOptions :KeycloakInitOptions = {
        onLoad: 'login-required',
        checkLoginIframe: false,
        timeSkew: 0,
        token: sessionStorage.getItem('KEYCLOAK_TOKEN'),
        refreshToken: sessionStorage.getItem('KEYCLOAK_REFRESH_TOKEN'),
        idToken: sessionStorage.getItem('KEYCLOAK_ID_TOKEN')
      }
      // Here we clear session storage, and add a flag in to prevent the app from
      // putting tokens back in from returning async calls  (see #2341)
      configHelper.clearSession()
      configHelper.addToSession(SessionStorageKeys.PreventStorageSync, true)
      return new Promise((resolve, reject) => {
        this.kc.init(kcOptions)
          .success(authenticated => {
            if (!authenticated) {
              resolve()
            }
            redirectUrl = redirectUrl || `${window.location.origin}${process.env.VUE_APP_PATH}`
            this.kc.logout({ redirectUri: redirectUrl })
              .success(() => {
                resolve()
              })
              .error(error => {
                reject(error)
              })
          })
          .error(error => {
            reject(error)
          })
      })
    }
  }

  getKCInstance () : KeycloakInstance {
    return this.kc
  }

  cleanupSession () {
    configHelper.removeFromSession(SessionStorageKeys.KeyCloakToken)
    configHelper.removeFromSession(SessionStorageKeys.KeyCloakRefreshToken)
    configHelper.removeFromSession(SessionStorageKeys.KeyCloakIdToken)
  }

  async refreshToken () {
    // Set the token expiry time as the minValidity to force refresh token
    let tokenExpiresIn = this.kc.tokenParsed['exp'] - Math.ceil(new Date().getTime() / 1000) + this.kc.timeSkew + 100
    this.kc.updateToken(tokenExpiresIn)
      .success(refreshed => {
        if (refreshed) {
          this.initSession()
        }
      })
      .error(() => {
        this.cleanupSession()
      })
  }

  verifyRoles (allowedRoles:[], disabledRoles:[]) {
    let isAuthorized = false
    if (allowedRoles || disabledRoles) {
      let userInfo = this.getUserInfo()
      isAuthorized = allowedRoles ? allowedRoles.some(role => userInfo.roles.includes(role)) : !disabledRoles.some(role => userInfo.roles.includes(role))
    } else {
      isAuthorized = true
    }
    return isAuthorized
  }

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

export default KeyCloakService.getInstance()
